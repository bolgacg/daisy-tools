import json, sys
for c in sys.argv[1:]:
    rows = [json.loads(l) for l in open(f"results/smoke_{c}.jsonl", encoding="utf-8")]
    print(f"--- {c}: {len(rows)} rows, mean s/row {sum(r['seconds'] for r in rows)/max(len(rows),1):.1f}")
    for r in rows[:3]:
        print("   gold:", r["gold"], "| pred:", r["prediction"][:60], "| query:", (r.get("tool_query") or "")[:45], "| top:", (r.get("titles") or [""])[0][:30])
    if c.startswith("agentic"):
        print("   calls:", sum(1 for r in rows if r.get("tool_query")), "| first outputs:", [ (r.get("first_output") or "")[:40] for r in rows[:4]])
