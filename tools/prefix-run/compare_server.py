#!/usr/bin/env python3
"""Compare a running llama-server's answers with a reference run (for example the official
transformers prefix-attention output) on the same questions.

Example:
  python tools/prefix-run/compare_server.py --ref results/pred_mimir-official-prefix-t100_closed.jsonl \
      --model mimir-prefix --n 40 --config nocache-nothink

Configs (request-level options, so no server restart is needed):
  default            cache_prompt on, template defaults (llama-server defaults)
  nocache            cache_prompt off
  nothink            chat_template_kwargs enable_thinking=false
  nocache-nothink    both
Prints the share of word-identical answers after the DAISY normaliser, and exact match for both.
"""
import argparse, json, re, string, sys, time, unicodedata
import requests

sys.path.insert(0, ".")
try:
    from daisy_tools.metrics import PROMPT_TEMPLATE, PROMPT_TEMPLATE_DFM, exact_match_score as em_fn, normalize_text as norm
except Exception:  # standalone use: same normaliser as dfm-evals daisy.py
    PROMPT_TEMPLATE = PROMPT_TEMPLATE_DFM = None
    def norm(s):
        s = (s or "").lower().strip()
        s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
        s = re.sub(r"[%s]" % re.escape(string.punctuation), " ", s)
        return " ".join(s.split())
    def em_fn(p, g):
        return float(norm(p) == norm(g))

CONFIGS = {
    "default": {},
    "nocache": {"cache_prompt": False},
    "nothink": {"chat_template_kwargs": {"enable_thinking": False}},
    "nocache-nothink": {"cache_prompt": False, "chat_template_kwargs": {"enable_thinking": False}},
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True, help="jsonl with id, question, gold, prediction")
    ap.add_argument("--base-url", default="http://127.0.0.1:8080")
    ap.add_argument("--model", default="mimir-prefix")
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--max-tokens", type=int, default=100)
    ap.add_argument("--config", default="default", choices=list(CONFIGS) + ["all"])
    ap.add_argument("--prompt-template", default=None, help="python format string with {question}; default: daisy_tools PROMPT_TEMPLATE")
    ap.add_argument("--template", default="sdu", choices=["sdu", "dfm"], help="sdu = the SDU-Daisy evaluation script's template (leading newline, two blank lines before the question; what the runner uses); dfm = the dfm-evals daisy task's copy (one blank line). The reference run must use the same one.")
    ap.add_argument("--out", default=None)
    ap.add_argument("--erase-slot", action="store_true", help="POST /slots/0?action=erase before every request (needs the slots endpoint)")
    ap.add_argument("--extra-body", default=None, help="JSON merged into every request body, e.g. '{\"top_k\": 1}'")
    a = ap.parse_args()
    tpl = a.prompt_template or (PROMPT_TEMPLATE_DFM if a.template == "dfm" else PROMPT_TEMPLATE)
    if tpl is None:
        sys.exit("no prompt template: pass --prompt-template or run from the daisy-tools root")
    ref = [json.loads(l) for l in open(a.ref)][: a.n]

    # template rendering and BOS check
    msgs = [{"role": "user", "content": "Hej"}]
    for kw in ({}, {"chat_template_kwargs": {"enable_thinking": False}}):
        r = requests.post(f"{a.base_url}/apply-template", json={"messages": msgs, **kw}, timeout=30).json()
        print(f"template {kw or 'default'}: {r.get('prompt')!r}")
    props = requests.get(f"{a.base_url}/props", timeout=30).json()
    print("server add_bos:", props.get("bos_token"), "| n_ctx:", props.get("default_generation_settings", {}).get("n_ctx"))

    try:  # how many prompt tokens the server actually used, against the HF chat template count
        from transformers import AutoTokenizer
        _tok = AutoTokenizer.from_pretrained("danish-foundation-models/DFM-Mimir")
        _m = [{"role": "user", "content": tpl.format(question=ref[0]["question"])}]
        _hf = len(_tok.apply_chat_template(_m, add_generation_prompt=True, tokenize=True, return_dict=True)["input_ids"])
        _j = requests.post(f"{a.base_url}/v1/chat/completions", json={"model": a.model, "messages": _m, "max_tokens": 1, "temperature": 0.0}, timeout=120).json()
        print("prompt tokens used by the server:", _j.get("usage", {}).get("prompt_tokens"), "| HF chat template:", _hf)
    except Exception as e:
        print("prompt-token check skipped:", type(e).__name__)

    configs = list(CONFIGS) if a.config == "all" else [a.config]
    for cfg in configs:
        extra = CONFIGS[cfg]
        rows, t0 = [], time.time()
        for r in ref:
            if a.erase_slot:
                requests.post(f"{a.base_url}/slots/0?action=erase", timeout=30)
            body = {"model": a.model, "messages": [{"role": "user", "content": tpl.format(question=r["question"])}],
                    "max_tokens": a.max_tokens, "temperature": 0.0, **extra, **(json.loads(a.extra_body) if a.extra_body else {})}
            j = requests.post(f"{a.base_url}/v1/chat/completions", json=body, timeout=300).json()
            pred = (j["choices"][0]["message"].get("content") or "").strip()
            rows.append({"id": r["id"], "question": r["question"], "gold": r["gold"], "prediction": pred, "ref": r["prediction"]})
        dt = time.time() - t0
        same = sum(norm(x["prediction"]) == norm(x["ref"]) for x in rows)
        em_s = sum(em_fn(x["prediction"], x["gold"]) for x in rows) / len(rows)
        em_r = sum(em_fn(x["ref"], x["gold"]) for x in rows) / len(rows)
        print(f"[{cfg}{'+erase' if a.erase_slot else ''}{'+extra' if a.extra_body else ''}] n={len(rows)} identical={same} ({100*same/len(rows):.0f}%) EM server={100*em_s:.1f} EM ref={100*em_r:.1f} {dt/len(rows):.2f} s/q")
        if a.out:
            with open(a.out.replace(".jsonl", f"_{cfg}.jsonl"), "w") as f:
                for x in rows:
                    f.write(json.dumps(x, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
