"""Run DAISY under three conditions against an OpenAI-compatible chat endpoint (llama-server, vLLM).

  A  closed   : the group's prompt, model answers from memory (reproduces their setting)
  B  retrieve : same prompt, plus top-k Danish Wikipedia intros for a query shaped from the question
  C  agentic  : model may emit exactly one tool call  SEARCH: <query>  or answer directly; one round

Every row is logged with prompt, raw output, tool query, retrieved titles, so failures can be read.
"""
import json, os, re, sys, time
import requests

from .metrics import PROMPT_TEMPLATE
from .query import shaped_lookup
from .wiki import lookup

AGENT_PREAMBLE = (
    "Du har adgang til ét værktøj: en søgning i dansk Wikipedia. Hvis du ikke er sikker på svaret, "
    "skriv PRÆCIS én linje af formen\nSEARCH: <søgeord>\nog intet andet. Ellers svar direkte.\n"
)
AGENT_FEWSHOT = AGENT_PREAMBLE + (
    "\nEksempler på brug af værktøjet (kun når du er usikker):\n"
    "Spørgsmål: Hvem tegnede Aarhus Rådhus?\nSEARCH: Aarhus Rådhus arkitekt\n"
    "Spørgsmål: I hvilket år udkom romanen Lykke-Per?\nSEARCH: Lykke-Per roman\n"
    "Spørgsmål: Hvad hedder Danmarks hovedstad?\nKøbenhavn\n"
)
SC_N, SC_TEMP = 5, 0.7

def _vote(answers):
    from .metrics import normalize_text
    import collections
    c = collections.Counter(normalize_text(a) for a in answers if a.strip())
    if not c:
        return answers[0] if answers else ""
    top = c.most_common(1)[0][0]
    for a in answers:  # return the original surface form of the winning normalised answer
        if normalize_text(a) == top:
            return a
    return answers[0]

LOGPROBS = False   # when True, token log-probabilities of the answer are stored in usage["lp"]

SEARCH_TOOL = [{"type": "function", "function": {"name": "search_wikipedia", "description": "Søg i dansk Wikipedia og få de første afsnit af de bedste artikler.",
    "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "søgeord"}}, "required": ["query"]}}}]

def _chat_tools(base_url, model, messages, max_tokens, temperature, api_key="none", timeout=180):
    """One turn with the search tool offered through the model's native tool format. Returns (text, tool_query|None, raw)."""
    body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature, "tools": SEARCH_TOOL, "tool_choice": "auto"}
    r = requests.post(f"{base_url}/chat/completions", timeout=timeout, headers={"Authorization": f"Bearer {api_key}"}, json=body)
    if r.status_code >= 400:
        raise RuntimeError(f"HTTP {r.status_code} from server: {r.text[:300]}")
    j = r.json(); msg = j["choices"][0]["message"]
    calls = msg.get("tool_calls") or []
    q = None
    if calls:
        try:
            q = json.loads(calls[0]["function"]["arguments"]).get("query")
        except Exception:
            q = calls[0]["function"].get("arguments")
    return (msg.get("content") or "").strip(), (q or None), msg

def _chat(base_url, model, messages, max_tokens, temperature, api_key="none", timeout=180):
    body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    if LOGPROBS:
        body["logprobs"] = True; body["top_logprobs"] = 1
    r = requests.post(f"{base_url}/chat/completions", timeout=timeout,
                      headers={"Authorization": f"Bearer {api_key}"}, json=body)
    if r.status_code >= 400:
        raise RuntimeError(f"HTTP {r.status_code} from server: {r.text[:300]}")
    j = r.json()
    usage = dict(j.get("usage", {}))
    if LOGPROBS:
        try:
            toks = j["choices"][0].get("logprobs", {}).get("content") or []
            usage["lp"] = [round(t.get("logprob", 0.0), 4) for t in toks]
            usage["tok"] = [t.get("token", "") for t in toks][:24]
        except Exception:
            usage["lp"] = None
    return (j["choices"][0]["message"]["content"] or "").strip(), usage

def _ctx_block(docs, chars):
    parts = []
    for t, e in docs:
        e = (e or "").strip().replace("\n", " ")
        parts.append(f"[{t}] {e[:chars]}")
    return "\n".join(parts)

def run(rows, condition, base_url, model, out_path, k=3, chars=900, max_tokens=64,
        temperature=0.0, resume=True, parallel=4, queries=None):
    done = set()
    if resume and os.path.exists(out_path):
        for l in open(out_path, encoding="utf-8"):
            try:
                done.add(json.loads(l)["id"])
            except Exception:
                pass
    out = open(out_path, "a", encoding="utf-8")
    t0 = time.time(); n = 0
    import threading
    from concurrent.futures import ThreadPoolExecutor
    lock = threading.Lock()
    todo = [r for r in rows if r["id"] not in done]

    def work(r):
        t_row = time.time()
        rec = {"id": r["id"], "condition": condition, "question": r["Question"], "gold": r["Answer"], "subject": r.get("Subject", "")}
        base_prompt = PROMPT_TEMPLATE.format(question=r["Question"])
        if condition == "closed":
            pred, usage = _chat(base_url, model, [{"role": "user", "content": base_prompt}], max_tokens, temperature)
        elif condition == "closed-sc":
            samples = []
            for _ in range(SC_N):
                a, usage = _chat(base_url, model, [{"role": "user", "content": base_prompt}], max_tokens, SC_TEMP)
                samples.append(a.replace("\n", " ").strip())
            rec["samples"] = samples
            pred = _vote(samples)
        elif condition in ("retrieve", "retrieve-oracle", "retrieve-given"):
            if condition == "retrieve-given":  # query written by another model (query generator / reader split)
                qs = (queries or {}).get(r["id"]) or []
                qs = qs if isinstance(qs, list) else [qs]
                used = " || ".join(qs); docs = []; seen = set()
                for q in qs:
                    for t, e in lookup(q, limit=k, chars=chars):
                        if t not in seen:
                            seen.add(t); docs.append((t, e))
                docs = docs[: max(k, 3) if len(qs) == 1 else 2 * k]
                if not docs:
                    docs, used2 = shaped_lookup(r["Question"], limit=k, chars=chars); rec["fallback"] = True
            elif condition == "retrieve":
                docs, used = shaped_lookup(r["Question"], limit=k, chars=chars)
            else:  # oracle query: the benchmark's own subject field, an upper bound on "asking" quality
                used = r["Subject"].rstrip(".")
                docs = lookup(used, limit=k, chars=chars)
            rec["tool_query"] = used; rec["titles"] = [t for t, _ in docs]
            prompt = "Baggrundsviden fra dansk Wikipedia:\n" + _ctx_block(docs, chars) + "\n\n" + base_prompt
            pred, usage = _chat(base_url, model, [{"role": "user", "content": prompt}], max_tokens, temperature)
        elif condition == "agentic-scaffold":
            # decide-then-act: a yes/no confidence question first, search only on "nej"
            ask = base_prompt + "\n\nVed du svaret på dette spørgsmål med sikkerhed? Svar kun ja eller nej."
            dec, usage = _chat(base_url, model, [{"role": "user", "content": ask}], 8, temperature)
            rec["decision"] = dec
            if re.match(r"\s*ja\b", dec.lower()):
                pred, usage = _chat(base_url, model, [{"role": "user", "content": base_prompt}], max_tokens, temperature)
            else:
                docs, used = shaped_lookup(r["Question"], limit=k, chars=chars)
                rec["tool_query"] = used; rec["titles"] = [t for t, _ in docs]
                prompt = "Baggrundsviden fra dansk Wikipedia:\n" + _ctx_block(docs, chars) + "\n\n" + base_prompt
                pred, usage = _chat(base_url, model, [{"role": "user", "content": prompt}], max_tokens, temperature)
        elif condition == "agentic-native":
            # the model's own tool-call format (chat template), one round: call -> tool result -> answer
            msgs = [{"role": "user", "content": base_prompt}]
            first, q, raw = _chat_tools(base_url, model, msgs, max_tokens, temperature)
            rec["first_output"] = first; rec["native_call"] = bool(q)
            usage = {}
            if q:
                rec["tool_query"] = q
                docs = lookup(q, limit=k, chars=chars)
                if not docs:
                    docs, _ = shaped_lookup(r["Question"], limit=k, chars=chars); rec["fallback"] = True
                rec["titles"] = [t for t, _ in docs]
                msgs.append({"role": "assistant", "content": raw.get("content") or "", "tool_calls": raw.get("tool_calls")})
                msgs.append({"role": "tool", "name": "search_wikipedia", "tool_call_id": (raw.get("tool_calls") or [{}])[0].get("id", "call_1"), "content": _ctx_block(docs, chars)})
                try:
                    pred, usage = _chat(base_url, model, msgs + [{"role": "user", "content": base_prompt}], max_tokens, temperature)
                except Exception as e:  # templates that refuse tool messages: fall back to plain context
                    rec["tool_turn_error"] = str(e)[:120]
                    prompt = "Søgeresultater fra dansk Wikipedia:\n" + _ctx_block(docs, chars) + "\n\n" + base_prompt
                    pred, usage = _chat(base_url, model, [{"role": "user", "content": prompt}], max_tokens, temperature)
            else:
                pred = first
        elif condition in ("agentic", "agentic-fewshot"):
            pre = AGENT_PREAMBLE if condition == "agentic" else AGENT_FEWSHOT
            first, usage = _chat(base_url, model, [{"role": "user", "content": pre + base_prompt}],
                                 max_tokens, temperature)
            rec["first_output"] = first
            m = re.search(r"SEARCH:\s*(.+)", first)
            if m:
                q = m.group(1).strip().splitlines()[0][:200]
                rec["tool_query"] = q
                docs = lookup(q, limit=k, chars=chars)
                if not docs:  # model's own query found nothing: fall back to the shaped question
                    docs, _ = shaped_lookup(r["Question"], limit=k, chars=chars); rec["fallback"] = True
                rec["titles"] = [t for t, _ in docs]
                prompt = ("Søgeresultater fra dansk Wikipedia:\n" + _ctx_block(docs, chars) +
                          "\n\n" + base_prompt)
                pred, usage2 = _chat(base_url, model, [{"role": "user", "content": prompt}], max_tokens, temperature)
            else:
                pred = first
        else:
            raise ValueError(condition)
        rec["prediction"] = pred.replace("\n", " ").strip()
        rec["usage"] = usage
        rec["seconds"] = round(time.time() - t_row, 2)
        return rec

    with ThreadPoolExecutor(max_workers=parallel) as ex:
        for rec in ex.map(work, todo):
            with lock:
                out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()
                n += 1
                if n % 50 == 0:
                    print(f"{condition}: {n}/{len(todo)} rows, {time.time()-t0:.0f}s", flush=True)
    out.close()
    return n

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("condition", choices=["closed", "closed-sc", "retrieve", "retrieve-oracle", "retrieve-given", "agentic", "agentic-fewshot", "agentic-scaffold", "agentic-native"])
    ap.add_argument("--data", default="data/daisy.jsonl")
    ap.add_argument("--base-url", default="http://127.0.0.1:8080/v1")
    ap.add_argument("--model", default="mimir")
    ap.add_argument("--out", default=None)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--max-tokens", type=int, default=64)
    ap.add_argument("--limit", type=int, default=0, help="only the first N rows (smoke test)")
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--logprobs", action="store_true")
    ap.add_argument("--queries-from", default=None, help="jsonl of a previous run; its tool_query per id is used (retrieve-given)")
    ap.add_argument("--wiki-lang", default="da")
    ap.add_argument("--chars", type=int, default=900)
    a = ap.parse_args()
    if a.logprobs:
        LOGPROBS = True
    if a.wiki_lang != "da":
        from . import wiki as _w; _w.set_lang(a.wiki_lang)
    queries = None
    if a.queries_from:
        queries = {}
        for path in a.queries_from.split(","):
            for l in open(path, encoding="utf-8"):
                d = json.loads(l)
                if d.get("tool_query") and not d.get("fallback"):
                    queries.setdefault(d["id"], []).append(d["tool_query"])
        print("loaded queries for", len(queries), "ids from", a.queries_from)
    rows = [json.loads(l) for l in open(a.data, encoding="utf-8")]
    if a.limit:
        rows = rows[: a.limit]
    out = a.out or f"results/pred_{a.model}_{a.condition}.jsonl"
    n = run(rows, a.condition, a.base_url, a.model, out, k=a.k, chars=a.chars, max_tokens=a.max_tokens, parallel=a.parallel, queries=queries)
    print("done", n, "rows ->", out)
