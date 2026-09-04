"""Assemble results/RESULTS.md: replication rows, retrieval ceilings, our runs (model x condition)."""
import glob, json, os, re, sys, collections
sys.path.insert(0, ".")
from daisy_tools.metrics import score_all

import random
def boot_ci(vals, n=1000, seed=4242):
    rnd = random.Random(seed); m = len(vals)
    if not m: return (float("nan"), float("nan"))
    means = sorted(sum(rnd.choice(vals) for _ in range(m)) / m for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n)]

def load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8")]

print("# DAISY with tools: results\n")
rep = "results/replication_big_models_public592.json"
if os.path.exists(rep):
    print("## Replication: the group's own predictions, rescored on the 592 public golds\n")
    print("| model | n | EM | F1 | BLEU | paper F1 | paper BLEU |\n|---|---|---|---|---|---|---|")
    for m, s in sorted(json.load(open(rep)).items(), key=lambda x: -x[1]["F1"]):
        print(f"| {m} | {s['n']} | {s['EM']:.3f} | {s['F1']:.3f} | {s['BLEU']:.3f} | {s.get('paper_f1')} | {s.get('paper_bleu')} |")
    print()
ceil = sorted(glob.glob("results/retrieval_ceiling_*.jsonl"))
if ceil:
    print("## Answer recall@3 (retrieval ceiling): gold answer literally inside the top-3 Danish Wikipedia intros\n")
    print("| query formulation | n | hit rate |\n|---|---|---|")
    for p in ceil:
        rows = load(p)
        modes = [k for k in rows[0] if k != "id"] if rows else []
        for m in modes:
            hits = sum(1 for r in rows if isinstance(r.get(m), dict) and r[m].get("hit"))
            print(f"| {m} ({os.path.basename(p)}) | {len(rows)} | {hits/len(rows):.3f} |")
    print()
preds = sorted(glob.glob("results/pred_*.jsonl"))
if preds:
    print("## Our runs: small models, greedy, zero-shot, the group's prompt and scorer\n")
    from daisy_tools.metrics import lenient_match, exact_match_score
    print("| model | condition | n | EM (SQuAD) | 95% CI | contains-gold acc. | F1 | BLEU | tool calls | fallback | s/row |\n|---|---|---|---|---|---|---|---|---|---|---|")
    for p in preds:
        m = re.match(r"results/pred_(.+)_(closed-sc|closed|retrieve-oracle|retrieve-rerank[a-z0-9+-]*|retrieve-title[a-z0-9+-]*|retrieve-plus[a-z0-9+-]*|retrieve-given-[a-z0-9+]+|retrieve-k[0-9]+|retrieve-c[0-9]+|retrieve-en|retrieve-local|retrieve|agentic-scaffold|agentic-fewshot|agentic-native|agentic-en|agentic-local|agentic)\.jsonl", p)
        if not m:
            continue
        rows = load(p)
        try:
            s = score_all([(r["prediction"], r["gold"]) for r in rows], with_bleu=True)
        except ModuleNotFoundError:
            s = score_all([(r["prediction"], r["gold"]) for r in rows], with_bleu=False); s["BLEU"] = float("nan")
        calls = sum(1 for r in rows if r.get("tool_query")); fb = sum(1 for r in rows if r.get("fallback"))
        len_em = sum(lenient_match(r["prediction"], r["gold"]) for r in rows) / max(len(rows), 1)
        secs = [r["seconds"] for r in rows if isinstance(r.get("seconds"), (int, float))]
        spr = sum(secs) / len(secs) if secs else float("nan")
        lo, hi = boot_ci([exact_match_score(r["prediction"], r["gold"]) for r in rows])
        print(f"| {m.group(1)} | {m.group(2)} | {s['n']} | {s['EM']:.3f} | {lo:.3f} to {hi:.3f} | {len_em:.3f} | {s['F1']:.3f} | {s['BLEU']:.3f} | {calls} | {fb} | {spr:.1f} |")
    print()
    print("## By answer type (EM)\n")
    def atype(a):
        a = a.strip()
        if a.isdigit() and len(a) == 4: return "year"
        if any(c.isdigit() for c in a): return "number"
        return "text"
    print("| model | condition | year | number | text |\n|---|---|---|---|---|")
    from daisy_tools.metrics import exact_match_score
    for p in preds:
        m = re.match(r"results/pred_(.+)_(closed-sc|closed|retrieve-oracle|retrieve-rerank[a-z0-9+-]*|retrieve-title[a-z0-9+-]*|retrieve-plus[a-z0-9+-]*|retrieve-given-[a-z0-9+]+|retrieve-k[0-9]+|retrieve-c[0-9]+|retrieve-en|retrieve-local|retrieve|agentic-scaffold|agentic-fewshot|agentic-native|agentic-en|agentic-local|agentic)\.jsonl", p)
        if not m: continue
        by = collections.defaultdict(list)
        for r in load(p):
            by[atype(r["gold"])].append(exact_match_score(r["prediction"], r["gold"]))
        cells = " | ".join(f"{sum(by[t])/len(by[t]):.3f} (n={len(by[t])})" if by[t] else "-" for t in ("year", "number", "text"))
        print(f"| {m.group(1)} | {m.group(2)} | {cells} |")

# --- Did the model know when to look? closed-book correctness vs the agentic decision to call ---
from daisy_tools.metrics import exact_match_score as _em
models = sorted({re.match(r"results/pred_(.+)_closed\.jsonl", p).group(1) for p in glob.glob("results/pred_*_closed.jsonl")})
if models:
    print("\n## Retrieval-necessity confusion matrix: did the model know when to look? (call decision vs closed-book EM)\n")
    print("Reading: 'called when wrong' is the useful call, 'silent when wrong' is the bluff, 'called when right' is wasted effort.\n")
    print("| model | agentic variant | called when wrong | silent when wrong | called when right | silent when right | call precision | call recall |\n|---|---|---|---|---|---|---|---|")
    for mname in models:
        closed = {r["id"]: _em(r["prediction"], r["gold"]) for r in load(f"results/pred_{mname}_closed.jsonl")}
        for var in ("agentic", "agentic-fewshot", "agentic-scaffold"):
            pth = f"results/pred_{mname}_{var}.jsonl"
            if not os.path.exists(pth): continue
            cw = sw = cr = sr = 0
            for r in load(pth):
                if r["id"] not in closed: continue
                right = closed[r["id"]] >= 1.0; called = bool(r.get("tool_query"))
                if called and not right: cw += 1
                elif not called and not right: sw += 1
                elif called and right: cr += 1
                else: sr += 1
            prec = cw / (cw + cr) if (cw + cr) else float("nan"); rec = cw / (cw + sw) if (cw + sw) else float("nan")
            print(f"| {mname} | {var} | {cw} | {sw} | {cr} | {sr} | {prec:.2f} | {rec:.2f} |")

# --- Reading fidelity: when retrieval did contain the gold answer, did the model extract it? ---
ceil_path = "results/retrieval_ceiling_k3_shaped.jsonl"
if os.path.exists(ceil_path):
    hit = {r["id"]: bool(r["shaped"]["hit"]) for r in load(ceil_path)}
    print("\n## Reader accuracy given retrieval success (reading fidelity) vs distraction: EM when the gold answer was inside the retrieved intros vs not (retrieve condition)\n")
    print("| model | EM given answer present | n | EM given answer absent | n |\n|---|---|---|---|---|")
    for p in sorted(glob.glob("results/pred_*_retrieve.jsonl")):
        mname = re.match(r"results/pred_(.+)_retrieve\.jsonl", p).group(1)
        a, b = [], []
        for r in load(p):
            (a if hit.get(r["id"]) else b).append(_em(r["prediction"], r["gold"]))
        print(f"| {mname} | {sum(a)/len(a) if a else float('nan'):.3f} | {len(a)} | {sum(b)/len(b) if b else float('nan'):.3f} | {len(b)} |")

# --- Can the model ask? quality of the model's own SEARCH queries in the agentic runs ---
def _norm_title(t):
    return re.sub(r"[^a-z0-9æøå]+", " ", (t or "").lower()).strip().rstrip(".")
ag = sorted(glob.glob("results/pred_*_agentic*.jsonl"))
if ag:
    print("\n## Can the model ask? Page-level precision of model-written queries (first Wikipedia hit is the subject page)\n")
    print("| model | variant | calls | first hit = subject | rate | empty results (fell back) |\n|---|---|---|---|---|---|")
    for p in ag:
        m = re.match(r"results/pred_(.+)_(agentic-fewshot|agentic)\.jsonl", p)
        if not m: continue
        rows = [r for r in load(p) if r.get("tool_query")]
        good = sum(1 for r in rows if r.get("titles") and _norm_title(r["titles"][0]) == _norm_title(r.get("subject", "")))
        fb = sum(1 for r in rows if r.get("fallback"))
        print(f"| {m.group(1)} | {m.group(2)} | {len(rows)} | {good} | {good/len(rows) if rows else float('nan'):.2f} | {fb} |")

# --- Default answers: the most repeated predictions per run (a model that does not know tends to name the same famous thing) ---
if preds:
    print("\n## Default answers: most repeated predictions per run\n")
    print("| model | condition | top repeated predictions (count) | share of rows |\n|---|---|---|---|")
    for p in preds:
        m = re.match(r"results/pred_(.+)_(closed-sc|closed|retrieve-oracle|retrieve-rerank[a-z0-9+-]*|retrieve-title[a-z0-9+-]*|retrieve-plus[a-z0-9+-]*|retrieve-given-[a-z0-9+]+|retrieve-k[0-9]+|retrieve-c[0-9]+|retrieve-en|retrieve-local|retrieve|agentic-scaffold|agentic-fewshot|agentic-native|agentic-en|agentic-local|agentic)\.jsonl", p)
        if not m: continue
        rows = load(p)
        c = collections.Counter(re.sub(r"[^a-z0-9æøå]+", " ", r["prediction"].lower()).strip() for r in rows)
        top = c.most_common(3)
        share = sum(n for _, n in top) / max(len(rows), 1)
        print(f"| {m.group(1)} | {m.group(2)} | " + "; ".join(f"{t[:28]} ({n})" for t, n in top) + f" | {share:.2f} |")


# --- Failure taxonomy with counts (rule-based; see scripts/failure_taxonomy.py) ---
import subprocess
print("\n## What goes wrong, counted (rule-based taxonomy; first matching category wins)\n")
print(subprocess.run([sys.executable, "scripts/failure_taxonomy.py"], capture_output=True, text=True).stdout)
print("\n## Cost axis: tokens, lookups and seconds per question; exact match per 1k tokens and per second\n")
print(subprocess.run([sys.executable, "scripts/cost_table.py"], capture_output=True, text=True).stdout)
