"""Regenerate results/popqa_summary.json from results/popqa_<model>_<cond>.jsonl (Self-RAG PopQA long-tail set).
match = share of rows whose prediction contains a gold answer; calls = rows where the model issued a search (tool_query)."""
import glob, json, os, re
out = {}
for p in sorted(glob.glob("results/popqa_*.jsonl")):
    m = re.match(r"results/popqa_(.+?)_(closed|ret5|ret10|agentic-en)\.jsonl", p)
    if not m:
        continue
    rows = [json.loads(l) for l in open(p)]
    if not rows:
        continue
    model, cond = m.group(1), m.group(2)
    out.setdefault(model, {})[cond] = {"match": sum(r.get("match", 0.0) for r in rows) / len(rows), "n": len(rows),
                                       "calls": sum(1 for r in rows if r.get("tool_query"))}
json.dump(out, open("results/popqa_summary.json", "w"), indent=1)
for model, v in out.items():
    print(model, {c: (round(100 * d["match"], 1), d["n"]) for c, d in v.items()})
