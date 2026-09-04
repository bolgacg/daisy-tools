"""How often does the gold answer literally appear in the top-k Danish Wikipedia intros?
Two query formulations: the question itself (what a model can do) and the Subject field (oracle)."""
import json, re, sys, time
sys.path.insert(0, ".")
from daisy_tools.wiki import lookup
from daisy_tools.query import shaped_lookup

def norm(s):
    return re.sub(r"[^a-z0-9æøå]+", " ", s.lower()).strip()

rows = [json.loads(l) for l in open("data/daisy.jsonl", encoding="utf-8")]
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 3
mode_set = sys.argv[2] if len(sys.argv) > 2 else "question,subject"
outp = f"results/retrieval_ceiling_k{limit}_{mode_set.replace(',','-')}.jsonl"
done = {}
if __import__("os").path.exists(outp):
    for l in open(outp, encoding="utf-8"):
        try:
            d = json.loads(l); done[d["id"]] = d
        except Exception:
            pass
out = open(outp, "a", encoding="utf-8")
hits = {m: 0 for m in mode_set.split(",")}; hits["either"] = 0
for d in done.values():
    for m in hits:
        if m != "either" and m in d:
            hits[m] += bool(d[m].get("hit"))
    hits["either"] += any(d[m].get("hit") for m in d if m != "id")
print(f"resuming with {len(done)} rows already done", flush=True)
t0 = time.time()
for i, r in enumerate(rows):
    if r["id"] in done:
        continue
    gold = norm(r["Answer"])
    rec = {"id": r["id"]}
    found = {}
    for mode in mode_set.split(","):
        if mode == "shaped":
            docs, used = shaped_lookup(r["Question"], limit=limit)
        else:
            used = r["Question"] if mode == "question" else r["Subject"].rstrip(".")
            docs = lookup(used, limit=limit)
        text = norm(" ".join(t + " " + e for t, e in docs))
        found[mode] = bool(gold) and gold in text
        rec[mode] = {"titles": [t for t, _ in docs], "hit": found[mode], "query": used}
        hits[mode] += found[mode]
    hits["either"] += any(found.values())
    out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()
    if (i + 1) % 50 == 0:
        print(f"{i+1}/{len(rows)} " + " ".join(f"{k}={v}" for k, v in hits.items()) + f" {time.time()-t0:.0f}s", flush=True)
n = len(rows)
print("FINAL", json.dumps({k: round(v / n, 3) for k, v in hits.items()}), f"n={n} k={limit}")
