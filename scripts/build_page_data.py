"""Emit site/data.json: aggregates for the charts and per-question rows for the browser.
Every number on the page comes from this file, which comes from results/*.jsonl."""
import glob, json, os, re, sys, collections
sys.path.insert(0, ".")
from daisy_tools.metrics import exact_match_score as em, f1_score, lenient_match, normalize_text

MODELS = {"mimir": "DFM Mimir 1B (llama.cpp, causal)", "mimir-hf": "DFM Mimir 1B (official, prefix attention)", "mimir-prefix": "DFM Mimir 1B (llama.cpp, patched prefix attention)", "llama1b": "Llama 3.2 1B", "llama3b": "Llama 3.2 3B", "gemma4b": "Gemma 3 4B", "qwen3b": "Qwen 2.5 3B"}
CONDS = ["closed", "closed-sc", "retrieve", "retrieve-oracle", "retrieve-given-gemma", "retrieve-given-qwen", "retrieve-given-gemma+qwen", "retrieve-k1", "retrieve-k5", "retrieve-c1800", "retrieve-en", "agentic", "agentic-fewshot", "agentic-scaffold", "agentic-native", "agentic-en", "retrieve-local", "retrieve-plus-local", "agentic-local", "agentic-native-local", "retrieve-k1-local", "retrieve-k5-local", "retrieve-c1800-local", "retrieve-wide-local", "retrieve-tworound-local"]
def load(p): return [json.loads(l) for l in open(p, encoding="utf-8")]
def atype(a):
    a = a.strip()
    return "year" if a.isdigit() and len(a) == 4 else ("number" if any(c.isdigit() for c in a) else "text")

gold = {r["id"]: r for r in load("data/daisy.jsonl")}
runs = {}   # (model, cond) -> {id: row}
for p in glob.glob("results/pred_*.jsonl"):
    m = re.match(r"results/pred_(.+?)_(closed-sc|closed|retrieve-oracle|retrieve-rerank[a-z0-9+-]*|retrieve-title[a-z0-9+-]*|retrieve-plus[a-z0-9+-]*|retrieve-given-[a-z0-9+]+|retrieve-k[0-9]+|retrieve-c[0-9]+|retrieve-en|retrieve-wide|retrieve-tworound|retrieve-local|retrieve|agentic-scaffold|agentic-fewshot|agentic-native|agentic-en|agentic-local|agentic)(-local)?\.jsonl", p)
    if not m or m.group(1) not in MODELS: continue
    runs[(m.group(1), m.group(2) + (m.group(3) or ""))] = {r["id"]: r for r in load(p)}

agg = []
for (mdl, cond), rows in sorted(runs.items()):
    vals = list(rows.values()); n = len(vals)
    if n < 100: continue   # skip empty or barely started runs (partial files from a running job)
    calls = sum(1 for r in vals if r.get("tool_query")); fb = sum(1 for r in vals if r.get("fallback"))
    by = collections.defaultdict(list)
    for r in vals: by[atype(r["gold"])].append(em(r["prediction"], r["gold"]))
    agg.append({"model": mdl, "cond": cond, "n": n,
                "em": sum(em(r["prediction"], r["gold"]) for r in vals) / n,
                "lenient": sum(lenient_match(r["prediction"], r["gold"]) for r in vals) / n,
                "f1": sum(f1_score(r["prediction"], r["gold"]) for r in vals) / n,
                "calls": calls, "fallback": fb,
                "sec": sum(r.get("seconds", 0) for r in vals) / n,
                "ptok": sum(((r.get("usage") or {}).get("prompt_tokens", 0)) for r in vals) / n,
                "otok": sum(((r.get("usage") or {}).get("completion_tokens", 0)) for r in vals) / n,
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
# offline-index ceilings: answer inside the three fetched intros (model independent: the query is the question)
loc_rows = runs.get(("gemma4b", "retrieve-local")) or next((v for (m, c), v in runs.items() if c == "retrieve-local"), None)
hit_local = {}
if loc_rows:
    hit_local = {i: bool(r.get("ctx_has_gold")) for i, r in loc_rows.items()}
    ceil["local"] = {"hit": sum(hit_local.values()) / len(hit_local), "n": len(hit_local), "by_id": hit_local}
# answer recall of every offline-index condition (for ceiling ticks: k=1, k=5, plus paragraphs, ten pages)
ceil_by_cond = {}
for (mdl, cond), rows in runs.items():
    if cond.endswith("-local") and rows and len(rows) >= 100 and any(r.get("ctx_has_gold") is not None for r in rows.values()):
        v = [bool(r.get("ctx_has_gold")) for r in rows.values()]
        ceil_by_cond.setdefault(cond, {"hit": sum(v) / len(v), "n": len(v)})
decomp = json.load(open("results/ceiling_decomp.json")) if os.path.exists("results/ceiling_decomp.json") else None
if decomp:
    ceil["local_pages"] = {"hit": (decomp["in_intros"] + decomp["below_intro"]) / decomp["n"], "n": decomp["n"], "by_id": {}}

# call decision 2x2 and reading fidelity
decision = []
for mdl in MODELS:
    closed = runs.get((mdl, "closed"))
    if not closed: continue
    for var in ("agentic", "agentic-fewshot", "agentic-scaffold", "agentic-native", "agentic-local", "agentic-native-local"):
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
fidelity_local = []
for mdl in MODELS:
    rows = runs.get((mdl, "retrieve-local"))
    if not rows or not hit_local or len(rows) < 100: continue
    a = [em(r["prediction"], r["gold"]) for i, r in rows.items() if hit_local.get(i)]
    b = [em(r["prediction"], r["gold"]) for i, r in rows.items() if not hit_local.get(i)]
    fidelity_local.append({"model": mdl, "n": len(rows), "em_present": sum(a) / len(a), "n_present": len(a), "em_absent": sum(b) / len(b), "n_absent": len(b)})
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

# Mimir, the same weights three ways (act one ruler table)
def _em_file(path):
    if not os.path.exists(path): return None
    rows = load(path); return {"em": sum(em(r["prediction"], r["gold"]) for r in rows) / len(rows), "n": len(rows)}
mimir_paths = [
    {"label": "Official implementation, prefix attention (as trained), fp16, 100 tokens", **(_em_file("results/pred_mimir-official-prefix-t100_closed.jsonl") or {})},
    {"label": "Official implementation, causal attention, fp16, 100 tokens", **(_em_file("results/pred_mimir-official-t100_closed.jsonl") or {})},
    {"label": "Community llama.cpp port (causal only), 8-bit, 64 tokens", **(_em_file("results/pred_mimir_closed.jsonl") or {})},
    {"label": "Community port with the prefix-attention fix built here, 8-bit, 100 tokens", **(_em_file("results/pred_mimir-prefix_closed.jsonl") or {})},
]
mimir_paths = [m for m in mimir_paths if "em" in m]
# the fixed port against the official implementation, same prompt bytes (tools/prefix-run/compare_server.py --template dfm)
port_check = None
if os.path.exists("results/portcheck_mimir-prefix_vs_official-dfm.jsonl"):
    pc = load("results/portcheck_mimir-prefix_vs_official-dfm.jsonl")
    port_check = {"n": len(pc), "identical": sum(normalize_text(r["prediction"] or "") == normalize_text(r["ref"] or "") for r in pc) / len(pc),
                  "em_port": sum(em(r["prediction"] or "", r["gold"]) for r in pc) / len(pc),
                  "em_official": sum(em(r["ref"] or "", r["gold"]) for r in pc) / len(pc)}
inspect_full = json.load(open("results/inspect_full_gemma4b.json")) if os.path.exists("results/inspect_full_gemma4b.json") else None
popqa = json.load(open("results/popqa_summary.json")) if os.path.exists("results/popqa_summary.json") else None
# their reading benchmark (multi_wiki_qa, dfm-evals protocol) and EuroEval, per model
mwqa = {}
for pth in glob.glob("results/mwqa_*.jsonl"):
    m = re.match(r"results/mwqa_(.+)\.jsonl", pth).group(1); rows = load(pth)
    if len(rows) >= 100:
        mwqa[m] = {"n": len(rows), "em": sum(float(r.get("em", 0)) for r in rows) / len(rows), "f1": sum(float(r.get("f1", 0)) for r in rows) / len(rows),
                   "sec": sum(r.get("seconds", 0) for r in rows) / len(rows)}
euroeval = {}
for pth in glob.glob("results/euroeval/*.jsonl"):
    for l in open(pth):
        d = json.loads(l); name = (d.get("model_info") or {}).get("name") or ""
        key = "gemma4b" if "gemma" in name else ("qwen3b" if "qwen" in name else ("llama3b" if "3b" in name.lower() and "llama" in name.lower() else name))
        sc = {e["evaluation_name"]: e["score_details"]["score"] for e in d.get("evaluation_results", [])}
        if sc: euroeval[key] = {"em": sc.get("test_em"), "f1": sc.get("test_f1"), "dataset": (d["evaluation_results"][0]["source_data"]["dataset_name"])}
# replication rows
rep = json.load(open("results/replication_big_models_public592.json")) if os.path.exists("results/replication_big_models_public592.json") else {}

# benchmark noise: questions where the gold is given away, unanswerable, or mangled by the official normaliser
def _nt(t): return re.sub(r"[^a-z0-9æøå]+", " ", (t or "").lower()).strip()
def flags_for(g):
    q, a = g["Question"], g["Answer"].strip(); f = []
    if _nt(a) and (" " + _nt(a) + " ") in (" " + _nt(q) + " "): f.append("leak")
    if a.lower().startswith("ukendt"): f.append("unknown")
    if not q.strip().endswith("?"): f.append("no_qmark")
    if " eller " in a or "/" in a: f.append("multi")
    if any(ord(c) > 127 for c in a): f.append("danish_letters")
    return f
noise_counts = collections.Counter()
for g in gold.values():
    for f in flags_for(g): noise_counts[f] += 1
noise = {"n": len(gold), "counts": dict(noise_counts)}
# per-question rows for the browser (compact)
qrows = []
for i, g in gold.items():
    q = {"id": i, "q": g["Question"], "gold": g["Answer"], "subject": g["Subject"], "type": atype(g["Answer"]), "hit_shaped": hit_shaped.get(i), "hit_local": hit_local.get(i), "flags": flags_for(g), "runs": {}}
    for (mdl, cond), rows in runs.items():
        r = rows.get(i)
        if not r: continue
        q["runs"][f"{mdl}|{cond}"] = {"p": r["prediction"][:120], "em": em(r["prediction"], r["gold"]),
                                      "len": lenient_match(r["prediction"], r["gold"]),
                                      "tq": (r.get("tool_query") or "")[:80], "top": (r.get("titles") or [""])[0][:60],
                                      "fb": bool(r.get("fallback")), "dec": (r.get("decision") or "")[:12]}
    qrows.append(q)

out = {"models": MODELS, "conds": CONDS, "agg": agg, "ceilings": {k: {"hit": v["hit"], "n": v["n"]} for k, v in ceil.items()},
       "decision": decision, "ceil_by_cond": ceil_by_cond, "fidelity": fidelity, "fidelity_local": fidelity_local, "decomp": decomp, "ask": askq, "replication": rep, "mimir_paths": mimir_paths, "port_check": port_check, "inspect_full": inspect_full, "popqa": popqa, "noise": noise, "mwqa": mwqa, "euroeval": euroeval, "questions": qrows,
       "paper": {"mimir_daisy_em_741": 9.6, "llama70b_f1_741": 0.268, "llama70b_bleu_741": 0.166}}
json.dump(out, open("site/data.json", "w", encoding="utf-8"), ensure_ascii=False)
open("site/data.js", "w", encoding="utf-8").write("window.DATA=" + json.dumps(out, ensure_ascii=False) + ";")
print("site/data.json:", round(os.path.getsize("site/data.json") / 1e6, 2), "MB;", len(agg), "aggregate rows;", len(qrows), "questions;", len(decision), "decision rows")
