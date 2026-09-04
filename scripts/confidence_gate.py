"""Does the model's own token confidence predict whether its closed-book answer is right, and what does a
confidence-gated lookup buy? Inputs: results/lp_<model>_closed.jsonl (with logprobs) and the retrieve run."""
import json, sys, math
sys.path.insert(0, ".")
from daisy_tools.metrics import exact_match_score as em

def auroc(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l]; neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg: return float("nan")
    wins = 0.0
    for p in pos:
        for q in neg:
            wins += 1.0 if p > q else (0.5 if p == q else 0.0)
    return wins / (len(pos) * len(neg))

for model in sys.argv[1:] or ["mimir"]:
    lp_rows = {r["id"]: r for r in (json.loads(l) for l in open(f"results/lp_{model}_closed.jsonl", encoding="utf-8"))}
    retr = {r["id"]: r for r in (json.loads(l) for l in open(f"results/pred_{model}_retrieve.jsonl", encoding="utf-8"))}
    ids = [i for i in lp_rows if i in retr and lp_rows[i]["usage"].get("lp")]
    right = [em(lp_rows[i]["prediction"], lp_rows[i]["gold"]) >= 1 for i in ids]
    feats = {
        "mean logprob": [sum(lp_rows[i]["usage"]["lp"]) / len(lp_rows[i]["usage"]["lp"]) for i in ids],
        "min logprob": [min(lp_rows[i]["usage"]["lp"]) for i in ids],
        "first-token logprob": [lp_rows[i]["usage"]["lp"][0] for i in ids],
        "sum logprob": [sum(lp_rows[i]["usage"]["lp"]) for i in ids],
    }
    print(f"\n== {model}: n={len(ids)}, closed-book right {sum(right)} ({sum(right)/len(ids):.1%})")
    for k, v in feats.items():
        print(f"  AUROC {k:22s} {auroc(v, right):.3f}")
    # gated system: answer from memory when confidence >= t, else use the retrieve answer
    conf = feats["min logprob"]; ret_right = [em(retr[i]["prediction"], retr[i]["gold"]) >= 1 for i in ids]
    print("  gate on min logprob: threshold | share answered from memory | EM of gated system | EM always-retrieve | EM never")
    for t in [0.0, -0.05, -0.1, -0.2, -0.3, -0.5, -1.0, -2.0, -99]:
        mem = [c >= t for c in conf]
        acc = sum((rr if m else tr) for m, rr, tr in zip(mem, right, ret_right)) / len(ids)
        print(f"    {t:6.2f} | {sum(mem)/len(ids):5.1%} | {acc:.3f} | {sum(ret_right)/len(ids):.3f} | {sum(right)/len(ids):.3f}")
