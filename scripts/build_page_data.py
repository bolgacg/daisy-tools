"""Emit site/data.json: aggregates for the charts and per-question rows for the browser.
Every number on the page comes from this file, which comes from results/*.jsonl."""
import glob, json, os, re, sys, collections
sys.path.insert(0, ".")
from daisy_tools.metrics import exact_match_score as em, f1_score, lenient_match

MODELS = {"mimir": "DFM Mimir 1B (llama.cpp, causal)", "mimir-hf": "DFM Mimir 1B (official, prefix attention)", "llama1b": "Llama 3.2 1B", "llama3b": "Llama 3.2 3B", "gemma4b": "Gemma 3 4B", "qwen3b": "Qwen 2.5 3B"}
CONDS = ["closed", "closed-sc", "retrieve", "retrieve-oracle", "retrieve-given-gemma", "retrieve-given-qwen", "retrieve-given-gemma+qwen", "retrieve-k1", "retrieve-k5", "retrieve-c1800", "retrieve-en", "agentic", "agentic-fewshot", "agentic-scaffold", "agentic-native", "agentic-en"]
def load(p): return [json.loads(l) for l in open(p, encoding="utf-8")]
def atype(a):
    a = a.strip()
    return "year" if a.isdigit() and len(a) == 4 else ("number" if any(c.isdigit() for c in a) else "text")

gold = {r["id"]: r for r in load("data/daisy.jsonl")}
runs = {}   # (model, cond) -> {id: row}
for p in glob.glob("results/pred_*.jsonl"):
    m = re.match(r"results/pred_(.+?)_(closed-sc|closed|retrieve-oracle|retrieve-rerank[a-z0-9+-]*|retrieve-title[a-z0-9+-]*|retrieve-given-[a-z0-9+]+|retrieve-k[0-9]+|retrieve-c[0-9]+|retrieve-en|retrieve-local|retrieve|agentic-scaffold|agentic-fewshot|agentic-native|agentic-en|agentic-local|agentic)\.jsonl", p)
    if not m or m.group(1) not in MODELS: continue
    runs[(m.group(1), m.group(2))] = {r["id"]: r for r in load(p)}

agg = []
for (mdl, cond), rows in sorted(runs.items()):
    vals = list(rows.values()); n = len(vals)
    calls = sum(1 for r in vals if r.get("tool_query")); fb = sum(1 for r in vals if r.get("fallback"))
    by = collections.defaultdict(list)
    for r in vals: by[atype(r["gold"])].append(em(r["prediction"], r["gold"]))
    agg.append({"model": mdl, "cond": cond, "n": n,
                "em": sum(em(r["prediction"], r["gold"]) for r in vals) / n,
                "lenient": sum(lenient_match(r["prediction"], r["gold"]) for r in vals) / n,
                "f1": sum(f1_score(r["prediction"], r["gold"]) for r in vals) / n,
                "calls": calls, "fallback": fb,
                "sec": sum(r.get("seconds", 0) for r in vals) / n,
                "by_type": {t: (sum(v) / len(v), len(v)) for t, v in by.items()}})

# ceilings
ceil = {}
for p, key in (("results/retrieval_ceiling_k3_question-subject.jsonl", None), ("results/retrieval_ceiling_k3_shaped.jsonl", None)):
    if os.path.exists(p):
        rows = load(p)
        for mode in [k for k in rows[0] if k != "id"]:
            ceil[mode] = {"hit": sum(1 for r in rows if r[mode].get("hit")) / len(rows), "n": len(rows),
                          "by_id": {r["id"]: bool(r[mode].get("hit")) for r in rows}}
hit_shaped = ceil.get("shaped", {}).get("by_id", {})

# call decision 2x2 and reading fidelity
decision = []
for mdl in MODELS:
    closed = runs.get((mdl, "closed"))
    if not closed: continue
    for var in ("agentic", "agentic-fewshot", "agentic-scaffold"):
        rows = runs.get((mdl, var))
        if not rows: continue
        c = collections.Counter()
        for i, r in rows.items():
            if i not in closed: continue
            right = em(closed[i]["prediction"], closed[i]["gold"]) >= 1; called = bool(r.get("tool_query"))
            c[("called" if called else "silent") + "_" + ("right" if right else "wrong")] += 1
        decision.append({"model": mdl, "variant": var, **{k: c.get(k, 0) for k in ("called_wrong", "silent_wrong", "called_right", "silent_right")}})
fidelity = []
for mdl in MODELS:
    rows = runs.get((mdl, "retrieve"))
    if not rows or not hit_shaped: continue
    a = [em(r["prediction"], r["gold"]) for i, r in rows.items() if hit_shaped.get(i)]
    b = [em(r["prediction"], r["gold"]) for i, r in rows.items() if not hit_shaped.get(i)]
    fidelity.append({"model": mdl, "em_present": sum(a) / len(a), "n_present": len(a), "em_absent": sum(b) / len(b), "n_absent": len(b)})
# query quality (agentic): first hit == subject
def nt(t): return re.sub(r"[^a-z0-9æøå]+", " ", (t or "").lower()).strip().rstrip(".")
askq = []
for (mdl, cond), rows in sorted(runs.items()):
    if not cond.startswith("agentic"): continue
    called = [r for r in rows.values() if r.get("tool_query") and not r.get("fallback")]
    if not called: continue
    good = sum(1 for r in called if r.get("titles") and nt(r["titles"][0]) == nt(r.get("subject") or gold[r["id"]]["Subject"]))
    own = sum(em(r["prediction"], r["gold"]) for r in called) / len(called)
    fbr = [r for r in rows.values() if r.get("fallback")]
    askq.append({"model": mdl, "variant": cond, "calls": len(called), "first_hit_subject": good, "em_own_query": own,
                 "fallbacks": len(fbr), "em_fallback": (sum(em(r["prediction"], r["gold"]) for r in fbr) / len(fbr)) if fbr else None})

# replication rows
rep = json.load(open("results/replication_big_models_public592.json")) if os.path.exists("results/replication_big_models_public592.json") else {}

# per-question rows for the browser (compact)
qrows = []
for i, g in gold.items():
    q = {"id": i, "q": g["Question"], "gold": g["Answer"], "subject": g["Subject"], "type": atype(g["Answer"]), "hit_shaped": hit_shaped.get(i), "runs": {}}
    for (mdl, cond), rows in runs.items():
        r = rows.get(i)
        if not r: continue
        q["runs"][f"{mdl}|{cond}"] = {"p": r["prediction"][:120], "em": em(r["prediction"], r["gold"]),
                                      "len": lenient_match(r["prediction"], r["gold"]),
                                      "tq": (r.get("tool_query") or "")[:80], "top": (r.get("titles") or [""])[0][:60],
                                      "fb": bool(r.get("fallback")), "dec": (r.get("decision") or "")[:12]}
    qrows.append(q)

out = {"models": MODELS, "conds": CONDS, "agg": agg, "ceilings": {k: {"hit": v["hit"], "n": v["n"]} for k, v in ceil.items()},
       "decision": decision, "fidelity": fidelity, "ask": askq, "replication": rep, "questions": qrows,
       "paper": {"mimir_daisy_em_741": 9.6, "llama70b_f1_741": 0.268, "llama70b_bleu_741": 0.166}}
json.dump(out, open("site/data.json", "w", encoding="utf-8"), ensure_ascii=False)
open("site/data.js", "w", encoding="utf-8").write("window.DATA=" + json.dumps(out, ensure_ascii=False) + ";")
print("site/data.json:", round(os.path.getsize("site/data.json") / 1e6, 2), "MB;", len(agg), "aggregate rows;", len(qrows), "questions;", len(decision), "decision rows")
