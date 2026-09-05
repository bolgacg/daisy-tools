"""Where the misses of the plain lookup go, on the full set. Titles are model independent (query = the question),
so any retrieve-local file works. Usage: python scripts/ceiling_decomp.py results/pred_gemma4b_retrieve-local.jsonl"""
import json, sys
from daisy_tools.metrics import normalize_text
from daisy_tools.localwiki import page, search
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
hit = below = miss = top10 = 0
for r in rows:
    gold = normalize_text(r["gold"]); titles = r.get("titles") or []
    if r.get("ctx_has_gold"):
        hit += 1; continue
    if any(gold and gold in normalize_text(page(t) or "") for t in titles):
        below += 1; continue
    miss += 1
    if any(gold and gold in normalize_text(page(t) or "") for t in search(r["question"], limit=10)[3:]):
        top10 += 1
n = len(rows)
print(f"n={n} answer in the 3 intros {hit} ({100*hit/n:.1f}%) | in a top-3 page below the intro {below} ({100*below/n:.1f}%) "
      f"| not in the top-3 pages {miss} ({100*miss/n:.1f}%), of which in ranks 4 to 10: {top10}")
