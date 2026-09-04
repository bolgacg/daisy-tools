"""Score prediction files with the group's metrics; per-condition and per-answer-type tables."""
import json, sys, collections
sys.path.insert(0, ".")
from daisy_tools.metrics import score_all, exact_match_score, f1_score

def atype(a):
    a = a.strip()
    if a.isdigit() and len(a) == 4: return "year"
    if any(c.isdigit() for c in a): return "number"
    return "text"

for path in sys.argv[1:]:
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    try:
        s = score_all([(r["prediction"], r["gold"]) for r in rows], with_bleu=True)
    except ModuleNotFoundError:
        s = score_all([(r["prediction"], r["gold"]) for r in rows], with_bleu=False)
    print(f"\n{path}: " + " ".join(f"{k}={v:.3f}" if isinstance(v, float) else f"{k}={v}" for k, v in s.items()))
    by = collections.defaultdict(list)
    for r in rows:
        by[atype(r["gold"])].append((exact_match_score(r["prediction"], r["gold"]), f1_score(r["prediction"], r["gold"])))
    for t, v in sorted(by.items()):
        print(f"  {t:7s} n={len(v):3d} EM={sum(x[0] for x in v)/len(v):.3f} F1={sum(x[1] for x in v)/len(v):.3f}")
    calls = sum(1 for r in rows if r.get("tool_query"))
    if calls:
        print(f"  tool calls: {calls}/{len(rows)} ({calls/len(rows):.1%}), fallbacks: {sum(1 for r in rows if r.get('fallback'))}")
