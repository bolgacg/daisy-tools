"""How often does the gold answer literally appear in the top-k Danish Wikipedia intros?
Two query formulations: the question itself (what a model can do) and the Subject field (oracle)."""
import json, re, sys, time
sys.path.insert(0, ".")
from daisy_tools.wiki import lookup

def norm(s):
    return re.sub(r"[^a-z0-9æøå]+", " ", s.lower()).strip()

rows = [json.loads(l) for l in open("data/daisy.jsonl", encoding="utf-8")]
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 3
out = open(f"results/retrieval_ceiling_k{limit}.jsonl", "w", encoding="utf-8")
hits = {"question": 0, "subject": 0, "either": 0}
t0 = time.time()
for i, r in enumerate(rows):
    gold = norm(r["Answer"])
    rec = {"id": r["id"]}
    found = {}
    for mode, q in (("question", r["Question"]), ("subject", r["Subject"].rstrip("."))):
        docs = lookup(q, limit=limit)
        text = norm(" ".join(t + " " + e for t, e in docs))
        found[mode] = bool(gold) and gold in text
        rec[mode] = {"titles": [t for t, _ in docs], "hit": found[mode]}
        hits[mode] += found[mode]
    hits["either"] += found["question"] or found["subject"]
    out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()
    if (i + 1) % 50 == 0:
        print(f"{i+1}/{len(rows)} question={hits['question']} subject={hits['subject']} either={hits['either']} {time.time()-t0:.0f}s", flush=True)
n = len(rows)
print("FINAL", json.dumps({k: round(v / n, 3) for k, v in hits.items()}), f"n={n} k={limit}")
