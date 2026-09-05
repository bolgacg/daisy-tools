"""Multi Wiki QA (Danish), the group's reading-with-context task, replicated from dfm-evals/tasks/multi_wiki_qa.py:
same source dataset, same filters, same seeded mini split (val 256, test 2048, train 1024, seed 4242), same prompt,
32 new tokens, greedy, same scorer (casefold, strip punctuation, strip a/an/the, max over references).
Backends: --backend server (llama-server OpenAI chat, one user message) or --backend hf (transformers, for Mimir).
"""
import time, argparse, json, os, random, re, string, sys, time
from collections import Counter
sys.path.insert(0, ".")

SRC = "oliverkinch/multi-wiki-qa-high-quality-subset"
PROMPT = "Tekst: {context}\n\nBesvar følgende spørgsmål om teksten ovenfor med maks. {max_words} ord.\n\nSpørgsmål: {question}"
SIZES = {"train": 1024, "val": 256, "test": 2048}
_ART = re.compile(r"\b(a|an|the)\b", re.UNICODE); _PUN = set(string.punctuation)

def norm(t):
    t = "".join(c for c in t.casefold() if c not in _PUN); return " ".join(_ART.sub(" ", t).split())
def em(p, refs): return max(float(norm(p) == norm(r)) for r in refs) if refs else 0.0
def f1(p, r):
    pt, rt = norm(p).split(), norm(r).split()
    if not pt and not rt: return 1.0
    if not pt or not rt: return 0.0
    ov = sum((Counter(pt) & Counter(rt)).values())
    if ov == 0: return 0.0
    pr, rc = ov / len(pt), ov / len(rt); return 2 * pr * rc / (pr + rc)
def maxf1(p, refs): return max(f1(p, r) for r in refs) if refs else 0.0

def load_split(split="test", seed=4242):
    cache = f"data/multiwikiqa_da_{split}.jsonl"
    if os.path.exists(cache):
        return [json.loads(l) for l in open(cache, encoding="utf-8")]
    from datasets import load_dataset
    try: ds = load_dataset(SRC, name="da", split="train")
    except ValueError: ds = load_dataset(SRC, split="train")
    recs = [dict(r) for r in ds]
    def ok(r):
        c, q = r.get("context"), r.get("question")
        if not isinstance(c, str) or not isinstance(q, str): return False
        if not (30 <= len(c) <= 5000) or not (10 <= len(q) <= 150): return False
        a = r.get("answers"); t = a.get("text") if isinstance(a, dict) else None
        t = [t] if isinstance(t, str) else t
        return bool(t) and any(isinstance(x, str) and x.strip() for x in t)
    recs = [r for r in recs if ok(r)]
    rng = random.Random(seed); idx = list(range(len(recs)))
    val = rng.sample(idx, SIZES["val"]); vs = set(val); rem = [i for i in idx if i not in vs]
    test = rng.sample(rem, SIZES["test"]); ts = set(test); rem2 = [i for i in rem if i not in ts]
    train = rng.sample(rem2, SIZES["train"])
    chosen = {"train": train, "val": val, "test": test}[split]
    out = []
    for j, i in enumerate(chosen):
        r = recs[i]; t = r["answers"]["text"]; t = [t] if isinstance(t, str) else t
        refs = []; seen = set()
        for x in t:
            if isinstance(x, str) and x.strip() and x.strip() not in seen: refs.append(x.strip()); seen.add(x.strip())
        out.append({"id": str(r.get("id") or f"da_{split}_{j}"), "context": r["context"], "question": r["question"], "refs": refs})
    os.makedirs("data", exist_ok=True)
    with open(cache, "w", encoding="utf-8") as f:
        for r in out: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="server", choices=["server", "hf"]); ap.add_argument("--model", default="model")
    ap.add_argument("--base-url", default="http://127.0.0.1:8080/v1"); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--parallel", type=int, default=3); ap.add_argument("--prefix", action="store_true"); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rows = load_split("test")
    if a.limit: rows = rows[: a.limit]
    out = a.out or f"results/mwqa_{a.model}.jsonl"
    done = {json.loads(l)["id"] for l in open(out, encoding="utf-8")} if os.path.exists(out) else set()
    todo = [r for r in rows if r["id"] not in done]
    fh = open(out, "a", encoding="utf-8"); t0 = time.time()
    if a.backend == "server":
        import requests
        from concurrent.futures import ThreadPoolExecutor
        def work(r):
            prompt = PROMPT.format(context=r["context"], question=r["question"], max_words=3)
            t1 = time.time()
            pred = None
            for attempt in range(3):  # a transient server error (e.g. CUDA OOM at start-up) must not kill the run
                try:
                    j = requests.post(f"{a.base_url}/chat/completions", timeout=300, json={"model": a.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 32, "temperature": 0}).json()
                    pred = (j["choices"][0]["message"]["content"] or "").strip(); break
                except Exception as e:  # noqa: BLE001
                    err = str(e)[:120]; time.sleep(20)
            if pred is None:
                pred = ""; print("row failed after 3 attempts:", err, file=sys.stderr)
            return {"id": r["id"], "prediction": pred, "refs": r["refs"], "em": em(pred, r["refs"]), "f1": maxf1(pred, r["refs"]), "usage": j.get("usage", {}), "seconds": round(time.time() - t1, 2)}
        with ThreadPoolExecutor(max_workers=a.parallel) as ex:
            for n, rec in enumerate(ex.map(work, todo), 1):
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); fh.flush()
                if n % 100 == 0: print(f"{n}/{len(todo)} {time.time()-t0:.0f}s", flush=True)
    else:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        name = "danish-foundation-models/DFM-Mimir"; dev = "cuda" if torch.cuda.is_available() else "cpu"
        tok = AutoTokenizer.from_pretrained(name); model = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float16 if dev == "cuda" else torch.float32, attn_implementation="sdpa").to(dev).eval()
        import inspect; tt = "token_type_ids" in inspect.signature(model.forward).parameters
        for n, r in enumerate(todo, 1):
            prompt = PROMPT.format(context=r["context"], question=r["question"], max_words=3)
            enc = tok.apply_chat_template([{"role": "user", "content": prompt}], add_generation_prompt=True, return_tensors="pt", return_dict=True)
            ids = (enc["input_ids"] if hasattr(enc, "keys") else enc).to(dev)
            kw = {"token_type_ids": torch.ones_like(ids)} if (a.prefix and tt) else {}
            t1 = time.time()
            with torch.no_grad(): g = model.generate(ids, max_new_tokens=32, do_sample=False, pad_token_id=tok.eos_token_id, **kw)
            pred = tok.decode(g[0][ids.shape[1]:], skip_special_tokens=True).strip()
            rec = {"id": r["id"], "prediction": pred, "refs": r["refs"], "em": em(pred, r["refs"]), "f1": maxf1(pred, r["refs"]), "seconds": round(time.time() - t1, 2), "impl": "hf" + ("-prefix" if a.prefix else "")}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); fh.flush()
            if n % 50 == 0: print(f"{n}/{len(todo)} {time.time()-t0:.0f}s", flush=True)
    fh.close()
    allrows = [json.loads(l) for l in open(out, encoding="utf-8")]
    print(f"{a.model}: n={len(allrows)} EM={sum(r['em'] for r in allrows)/len(allrows):.4f} F1={sum(r['f1'] for r in allrows)/len(allrows):.4f} -> {out}")

if __name__ == "__main__":
    main()
