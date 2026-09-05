#!/usr/bin/env python3
"""First-step comparison: for each question, the top-5 next tokens after the prompt, from a running llama-server
(/completion with the exact HF token ids, so no chat layer) and from the driver's --dump-top output.
Usage: python tools/prefix-run/step1_compare.py --prompts results/dev/prompts_dfm.jsonl --driver results/dev/driver60_dump.jsonl [--n 60]
"""
import argparse, json, math, requests

ap = argparse.ArgumentParser()
ap.add_argument("--prompts", required=True); ap.add_argument("--driver", required=True)
ap.add_argument("--base-url", default="http://127.0.0.1:8080"); ap.add_argument("--n", type=int, default=60)
ap.add_argument("--show", type=int, default=6, help="print this many questions whose first token differs")
a = ap.parse_args()
P = {r["id"]: r for r in map(json.loads, open(a.prompts))}
D = {r["id"]: r for r in map(json.loads, open(a.driver))}
ids = [i for i in D if i in P][: a.n]
diff_first, shown, close = 0, 0, 0
for i in ids:
    body = {"prompt": P[i]["ids"], "n_predict": 1, "n_probs": 5, "temperature": 0.0, "cache_prompt": False}
    j = requests.post(f"{a.base_url}/completion", json=body, timeout=120).json()
    cp = j.get("completion_probabilities") or []
    if not cp:
        print("no completion_probabilities in response; keys:", list(j)[:12]); break
    top = cp[0].get("top_logprobs") or cp[0].get("probs") or []
    s_top = [(t.get("id"), round(t.get("logprob", math.log(max(t.get("prob", 1e-30), 1e-30))), 3), t.get("token")) for t in top]
    d_top = [(t[0], round(t[1], 3), t[2]) for t in D[i]["top1"]]
    s_first = s_top[0][0] if s_top else None
    d_first = d_top[0][0]
    if s_first != d_first:
        diff_first += 1
        if shown < a.show:
            shown += 1
            print(f"\n{P[i].get('question', i)[:80]}\n  server top5: {s_top}\n  driver top5: {d_top}")
    else:
        # same first token: how far apart are the log-probs of the top-1?
        if s_top and abs(s_top[0][1] - d_top[0][1]) > 0.05: close += 1
print(f"\nfirst token differs on {diff_first} of {len(ids)}; same first token but top-1 logprob differs by >0.05 on {close}")
