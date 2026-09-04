"""Cost axis for every run: prompt tokens, completion tokens, retrieval calls and seconds per question,
plus exact match per 1000 tokens and per second. Reads results/pred_*.jsonl (usage fields from llama-server)."""
import glob, json, re, sys
sys.path.insert(0, ".")
from daisy_tools.metrics import exact_match_score as em
rows_out = []
for p in sorted(glob.glob("results/pred_*.jsonl")):
    m = re.match(r"results/pred_([^_]+)_(.+)\.jsonl", p)
    if not m: continue
    rows = [json.loads(l) for l in open(p, encoding="utf-8")]
    if not rows: continue
    n = len(rows)
    pt = sum((r.get("usage") or {}).get("prompt_tokens", 0) for r in rows) / n
    ct = sum((r.get("usage") or {}).get("completion_tokens", 0) for r in rows) / n
    calls = sum(1 for r in rows if r.get("tool_query")) / n
    sec = sum(r.get("seconds", 0) for r in rows) / n
    e = sum(em(r["prediction"], r["gold"]) for r in rows) / n
    tok = pt + ct
    rows_out.append((m.group(1), m.group(2), n, e, pt, ct, calls, sec, (e * 1000 / tok) if tok else float("nan"), (e / sec) if sec else float("nan")))
print("| model | condition | n | EM | prompt tok/q | completion tok/q | lookups/q | s/q | EM per 1k tok | EM per s |\n|---|---|---|---|---|---|---|---|---|---|")
for r in sorted(rows_out, key=lambda x: (-x[3])):
    print(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]:.3f} | {r[4]:.0f} | {r[5]:.1f} | {r[6]:.2f} | {r[7]:.1f} | {r[8]:.2f} | {r[9]:.3f} |")
