#!/usr/bin/env python3
"""Where does the server diverge from the driver during generation? Same HF token ids, greedy, 100 tokens.
P1: /completion with the exact ids (no chat layer), return_tokens -> first divergent step vs the driver's gen_ids.
P2: /v1/chat/completions first-token top-5 vs the driver's top-5 (is the chat layer's prompt the same?).
P3: /completion with samplers=["temperature"] only.
Usage: python tools/prefix-run/gen_compare.py --prompts results/dev/prompts_dfm.jsonl --driver results/dev/driver60_dump.jsonl --ref results/pred_mimir-official-prefix-t100_closed.jsonl
"""
import argparse, json, requests, sys
sys.path.insert(0, ".")
from daisy_tools.metrics import normalize_text as nt, PROMPT_TEMPLATE

ap = argparse.ArgumentParser()
ap.add_argument("--prompts", required=True); ap.add_argument("--driver", required=True); ap.add_argument("--ref", required=True)
ap.add_argument("--base-url", default="http://127.0.0.1:8080"); ap.add_argument("--model", default="mimir-prefix"); ap.add_argument("--n", type=int, default=60)
a = ap.parse_args()
P = {r["id"]: r for r in map(json.loads, open(a.prompts))}
D = {r["id"]: r for r in map(json.loads, open(a.driver))}
O = {r["id"]: r for r in map(json.loads, open(a.ref))}
ids = [i for i in D if i in P and i in O][: a.n]

def completion(i, extra):
    body = {"prompt": P[i]["ids"], "n_predict": 100, "temperature": 0.0, "cache_prompt": False, "return_tokens": True, **extra}
    return requests.post(f"{a.base_url}/completion", json=body, timeout=300).json()

for label, extra in (("P1 /completion ids", {}), ("P3 /completion ids, samplers=[temperature]", {"samplers": ["temperature"]})):
    same_off, same_drv, shown, steps = 0, 0, 0, []
    for i in ids:
        j = completion(i, extra)
        text = (j.get("content") or "").strip(); toks = j.get("tokens") or []
        same_off += nt(text) == nt(O[i]["prediction"]); d_ids = D[i]["gen_ids"]
        k = next((s for s in range(min(len(toks), len(d_ids))) if toks[s] != d_ids[s]), None)
        if toks[:len(d_ids)] == d_ids[:len(toks)] and len(toks) in (len(d_ids), len(d_ids) + 1): same_drv += 1
        else:
            steps.append(k if k is not None else min(len(toks), len(d_ids)))
            if shown < 3:
                shown += 1
                print(f"  [{label}] {O[i]["question"][:70]!r}\n     server: {text[:60]!r} tokens {toks[:8]}\n     driver: {D[i]['prediction'][:60]!r} tokens {d_ids[:8]}  first divergent step: {k}")
    print(f"{label}: identical to official {same_off}/{len(ids)}; same token sequence as driver {same_drv}/{len(ids)}; divergence steps {sorted(steps)[:20]}")

# P2: chat path, first token top-5
diff = 0
for i in ids:
    body = {"model": a.model, "messages": [{"role": "user", "content": PROMPT_TEMPLATE.format(question=O[i]["question"])}],
            "max_tokens": 1, "temperature": 0.0, "logprobs": True, "top_logprobs": 5}
    j = requests.post(f"{a.base_url}/v1/chat/completions", json=body, timeout=120).json()
    try:
        top = j["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
        s_first = top[0]["token"]; s_lp = top[0]["logprob"]
    except Exception as e:
        print("P2 parse failed:", type(e).__name__, str(j)[:200]); break
    d_first, d_lp, d_piece = D[i]["top1"][0]
    if s_first != d_piece or abs(s_lp - d_lp) > 0.05:
        diff += 1
        if diff <= 3: print(f"  [P2] {O[i]["question"][:60]!r} server first {s_first!r} {s_lp:.3f} | driver {d_piece!r} {d_lp:.3f}")
print(f"P2 chat path first token differs (token or logprob >0.05) on {diff}/{len(ids)}")
