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

def _chat(base_url, model, messages, max_tokens, temperature, api_key="none", timeout=180):
    r = requests.post(f"{base_url}/chat/completions", timeout=timeout,
                      headers={"Authorization": f"Bearer {api_key}"},
                      json={"model": model, "messages": messages, "max_tokens": max_tokens,
                            "temperature": temperature})
    if r.status_code >= 400:
        raise RuntimeError(f"HTTP {r.status_code} from server: {r.text[:300]}")
    j = r.json()
    return (j["choices"][0]["message"]["content"] or "").strip(), j.get("usage", {})

def _ctx_block(docs, chars):
    parts = []
    for t, e in docs:
        e = (e or "").strip().replace("\n", " ")
        parts.append(f"[{t}] {e[:chars]}")
    return "\n".join(parts)

def run(rows, condition, base_url, model, out_path, k=3, chars=900, max_tokens=64,
        temperature=0.0, resume=True, parallel=4):
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
        elif condition in ("retrieve", "retrieve-oracle"):
            if condition == "retrieve":
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
    ap.add_argument("condition", choices=["closed", "closed-sc", "retrieve", "retrieve-oracle", "agentic", "agentic-fewshot", "agentic-scaffold"])
    ap.add_argument("--data", default="data/daisy.jsonl")
    ap.add_argument("--base-url", default="http://127.0.0.1:8080/v1")
    ap.add_argument("--model", default="mimir")
    ap.add_argument("--out", default=None)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--max-tokens", type=int, default=64)
    ap.add_argument("--limit", type=int, default=0, help="only the first N rows (smoke test)")
    ap.add_argument("--parallel", type=int, default=4)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.data, encoding="utf-8")]
    if a.limit:
        rows = rows[: a.limit]
    out = a.out or f"results/pred_{a.model}_{a.condition}.jsonl"
    n = run(rows, a.condition, a.base_url, a.model, out, k=a.k, max_tokens=a.max_tokens, parallel=a.parallel)
    print("done", n, "rows ->", out)
