"""PopQA long-tail (1,399 questions) with the passages released by Self-RAG (Contriever top-10 plus web), the
"identical inputs" record: same questions, same passages, same metric (match: any gold alias inside the normalised
prediction, as in Self-RAG's run_short_form.py --metric match). Conditions: closed, ret5, ret10 (passages prepended),
agentic-en (our English Wikipedia tool, one round)."""
import argparse, ast, json, os, re, string, sys, time
sys.path.insert(0, ".")
DATA = os.path.expanduser("~/data/selfrag/popqa_longtail.jsonl")

def normalize_answer(s):
    s = s.lower(); s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = re.sub(r"\b(a|an|the)\b", " ", s); return " ".join(s.split())
def match(pred, answers):
    p = normalize_answer(pred); return float(any(normalize_answer(a) in p for a in answers))

def load():
    rows = []
    for l in open(DATA, encoding="utf-8"):
        d = json.loads(l)
        ans = d["answers"]; ans = ast.literal_eval(ans) if isinstance(ans, str) else ans
        ctx = d.get("ctxs"); ctx = ast.literal_eval(ctx) if isinstance(ctx, str) else ctx
        rows.append({"id": str(d.get("id")), "question": d["question"], "answers": ans, "ctxs": ctx or [], "pop": d.get("pop"), "prop": d.get("prop")})
    return rows

INSTR = "Answer the question with a short answer only, no explanation."
def prompt_for(r, cond):
    if cond == "closed":
        return f"{INSTR}\n\nQuestion: {r['question']}\nAnswer:"
    n = int(cond[3:])
    paras = "\n".join(f"[{i+1}] {c.get('title','')}: {c.get('text','').strip()}" for i, c in enumerate(r["ctxs"][:n]))
    return f"{INSTR} Use the passages below if they help.\n\nPassages:\n{paras}\n\nQuestion: {r['question']}\nAnswer:"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cond", choices=["closed", "ret5", "ret10", "agentic-en"])
    ap.add_argument("--model", required=True); ap.add_argument("--base-url", default="http://127.0.0.1:8080/v1")
    ap.add_argument("--parallel", type=int, default=3); ap.add_argument("--limit", type=int, default=0); ap.add_argument("--max-tokens", type=int, default=48)
    a = ap.parse_args()
    rows = load()
    if a.limit: rows = rows[: a.limit]
    out = f"results/popqa_{a.model}_{a.cond}.jsonl"
    done = {json.loads(l)["id"] for l in open(out, encoding="utf-8")} if os.path.exists(out) else set()
    todo = [r for r in rows if r["id"] not in done]
    import requests
    from concurrent.futures import ThreadPoolExecutor
    if a.cond == "agentic-en":
        from daisy_tools import wiki as _w; _w.set_lang("en")
        from daisy_tools.wiki import lookup
    def chat(msgs, mt):
        j = requests.post(f"{a.base_url}/chat/completions", timeout=300, json={"model": a.model, "messages": msgs, "max_tokens": mt, "temperature": 0}).json()
        return (j["choices"][0]["message"]["content"] or "").strip(), j.get("usage", {})
    def work(r):
        t1 = time.time(); rec = {"id": r["id"], "question": r["question"], "answers": r["answers"], "pop": r["pop"], "cond": a.cond}
        if a.cond == "agentic-en":
            pre = ("You have one tool: a search in English Wikipedia. If you are not sure of the answer, write EXACTLY one line of the form\nSEARCH: <query>\nand nothing else. Otherwise answer directly.\n")
            first, usage = chat([{"role": "user", "content": pre + prompt_for(r, "closed")}], a.max_tokens)
            rec["first_output"] = first
            m = re.search(r"SEARCH:\s*(.+)", first)
            if m:
                q = m.group(1).strip().splitlines()[0][:200]; rec["tool_query"] = q
                docs = lookup(q, limit=3, chars=900); rec["titles"] = [t for t, _ in docs]
                paras = "\n".join(f"[{i+1}] {t}: {e.strip()}" for i, (t, e) in enumerate(docs))
                pred, usage = chat([{"role": "user", "content": f"{INSTR} Use the passages below if they help.\n\nPassages:\n{paras}\n\nQuestion: {r['question']}\nAnswer:"}], a.max_tokens)
            else:
                pred = first
        else:
            pred, usage = chat([{"role": "user", "content": prompt_for(r, a.cond)}], a.max_tokens)
        rec["prediction"] = pred.replace("\n", " ").strip(); rec["match"] = match(rec["prediction"], r["answers"])
        rec["usage"] = usage; rec["seconds"] = round(time.time() - t1, 2); return rec
    fh = open(out, "a", encoding="utf-8"); t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.parallel) as ex:
        for n, rec in enumerate(ex.map(work, todo), 1):
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); fh.flush()
            if n % 100 == 0: print(f"{n}/{len(todo)} {time.time()-t0:.0f}s", flush=True)
    fh.close()
    allrows = [json.loads(l) for l in open(out, encoding="utf-8")]
    print(f"{a.model} {a.cond}: n={len(allrows)} match={sum(r['match'] for r in allrows)/len(allrows):.4f} -> {out}")

if __name__ == "__main__":
    main()
