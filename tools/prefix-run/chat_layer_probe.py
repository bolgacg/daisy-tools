#!/usr/bin/env python3
"""Why does /v1/chat/completions differ from /completion with the same ids? Three checks against a running server.
P2: chat path first-token top-5 vs the driver's --dump-top.  P4: /completion with the /apply-template STRING.
P8: chat request with verbose=true -> the prompt text the server actually used, diffed against the HF rendering."""
import argparse, difflib, json, requests, sys
sys.path.insert(0, ".")
from daisy_tools.metrics import normalize_text as nt, PROMPT_TEMPLATE
ap = argparse.ArgumentParser()
ap.add_argument("--data", default="data/daisy.jsonl"); ap.add_argument("--prompts", required=True); ap.add_argument("--driver", required=True); ap.add_argument("--ref", required=True)
ap.add_argument("--base-url", default="http://127.0.0.1:8080"); ap.add_argument("--model", default="mimir-prefix"); ap.add_argument("--n", type=int, default=60)
a = ap.parse_args()
Q = {r["id"]: r["Question"] for r in map(json.loads, open(a.data))}
P = {r["id"]: r for r in map(json.loads, open(a.prompts))}
D = {r["id"]: r for r in map(json.loads, open(a.driver))}
O = {r["id"]: r for r in map(json.loads, open(a.ref))}
ids = [i for i in D if i in P and i in O and i in Q][: a.n]
msgs = lambda i: [{"role": "user", "content": PROMPT_TEMPLATE.format(question=Q[i])}]

# P8: what prompt does the chat path really use?
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("danish-foundation-models/DFM-Mimir")
i0 = ids[0]
hf = tok.apply_chat_template(msgs(i0), add_generation_prompt=True, tokenize=False)
j = requests.post(f"{a.base_url}/v1/chat/completions", json={"model": a.model, "messages": msgs(i0), "max_tokens": 1, "temperature": 0.0, "verbose": True}, timeout=120).json()
used = (j.get("__verbose") or {}).get("prompt")
print("P8 __verbose keys:", list((j.get("__verbose") or {}).keys())[:12])
print("P8 HF rendering  :", repr(hf)[:400])
print("P8 server used   :", repr(used)[:400])
if used is not None:
    print("P8 equal after stripping a leading <bos>:", used.replace("<bos>", "", 1) == hf.replace("<bos>", "", 1))
    for l in difflib.unified_diff(hf.splitlines(), (used or "").splitlines(), "hf", "server", lineterm="", n=0): print("   ", l[:160])
tpl = requests.post(f"{a.base_url}/apply-template", json={"messages": msgs(i0)}, timeout=30).json().get("prompt")
print("P8 /apply-template equals HF (minus <bos>):", (tpl or "") == hf.replace("<bos>", "", 1))

# P2: chat path first token vs driver
diff = 0
for i in ids:
    j = requests.post(f"{a.base_url}/v1/chat/completions", json={"model": a.model, "messages": msgs(i), "max_tokens": 1, "temperature": 0.0, "logprobs": True, "top_logprobs": 5}, timeout=120).json()
    try:
        top = j["choices"][0]["logprobs"]["content"][0]["top_logprobs"]; s_first, s_lp = top[0]["token"], top[0]["logprob"]
    except Exception as e:
        print("P2 parse failed:", type(e).__name__, str(j)[:200]); break
    d_first, d_lp, d_piece = D[i]["top1"][0]
    if s_first != d_piece or abs(s_lp - d_lp) > 0.05:
        diff += 1
        if diff <= 3: print(f"  [P2] {Q[i][:60]!r} server first {s_first!r} {s_lp:.3f} | driver {d_piece!r} {d_lp:.3f}")
print(f"P2 chat path first token differs (token or logprob >0.05) on {diff}/{len(ids)}")

# P4: /completion with the rendered STRING
same_off = same_drv = 0
for i in ids:
    s = requests.post(f"{a.base_url}/apply-template", json={"messages": msgs(i)}, timeout=30).json()["prompt"]
    j = requests.post(f"{a.base_url}/completion", json={"prompt": s, "n_predict": 100, "temperature": 0.0, "cache_prompt": False, "return_tokens": True}, timeout=300).json()
    text = (j.get("content") or "").strip(); toks = j.get("tokens") or []; d_ids = D[i]["gen_ids"]
    same_off += nt(text) == nt(O[i]["prediction"]); same_drv += toks[:len(d_ids)] == d_ids[:len(toks)]
print(f"P4 /completion with the rendered string: identical to official {same_off}/{len(ids)}; same tokens as driver {same_drv}/{len(ids)}; prompt_n first = {j.get('tokens_evaluated') or (j.get('timings') or {}).get('prompt_n')}")
