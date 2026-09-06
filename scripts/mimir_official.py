"""Calibration run: DFM Mimir through the official transformers path (full weights, fp16 on the GPU),
closed book, the DAISY prompt, greedy, so the number can be compared with the paper's 9.6 and with our
llama.cpp Q8 run (5.6). Usage: python scripts/mimir_official.py [--limit N] [--cpu]"""
import argparse, json, os, sys, time
sys.path.insert(0, ".")
from daisy_tools.metrics import PROMPT_TEMPLATE, PROMPT_TEMPLATE_DFM, exact_match_score, lenient_match
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0); ap.add_argument("--cpu", action="store_true")
ap.add_argument("--max-new", type=int, default=100); ap.add_argument("--out", default=None)
ap.add_argument("--prefix", action="store_true", help="bidirectional prompt attention via token_type_ids=1 (prefix-LM)")
ap.add_argument("--attn", default="sdpa"); ap.add_argument("--dtype", default=None, choices=["float16","bfloat16","float32"], help="override the default (fp16 on GPU, fp32 on CPU)")
ap.add_argument("--template", default="dfm", choices=["dfm", "repo", "lab"], help="dfm = dfm-evals daisy.py template (their Inspect run); repo = SDU-Daisy eval.py template; lab = schneiderkamplab/dfm-evals dfm7.py sdu-daisy template (64 tokens, lowercase exact)")
a = ap.parse_args()
if a.out is None:
    a.out = f"results/pred_mimir-official{'-prefix' if a.prefix else ''}-t{a.max_new}{'' if a.template == 'dfm' else '-' + a.template}_closed.jsonl"
name = "danish-foundation-models/DFM-Mimir"
dev = "cpu" if a.cpu or not torch.cuda.is_available() else "cuda"
dtype = getattr(torch, a.dtype) if a.dtype else (torch.float32 if dev == "cpu" else torch.float16)
tok = AutoTokenizer.from_pretrained(name)
model = AutoModelForCausalLM.from_pretrained(name, dtype=dtype, attn_implementation=a.attn).to(dev).eval()
import inspect
accepts_tt = "token_type_ids" in inspect.signature(model.forward).parameters
print("forward accepts token_type_ids:", accepts_tt, "| prefix mode requested:", a.prefix, "| prefix_lm in config:", getattr(model.config, "prefix_lm", None), flush=True)
print("loaded", name, dev, dtype, "params", sum(p.numel() for p in model.parameters()) / 1e9, flush=True)
rows = [json.loads(l) for l in open("data/daisy.jsonl", encoding="utf-8")]
if a.limit: rows = rows[: a.limit]
done = set()
if os.path.exists(a.out):
    done = {json.loads(l)["id"] for l in open(a.out, encoding="utf-8")}
out = open(a.out, "a", encoding="utf-8"); t0 = time.time(); n = 0; ems = []
for r in rows:
    if r["id"] in done: continue
    PROMPT_TEMPLATE_LAB = "Besvar spørgsmålet kort og præcist på dansk.\n\nSpørgsmål:\n{question}"  # schneiderkamplab/dfm-evals dfm7.py QA_DA_PROMPT
    tpl = PROMPT_TEMPLATE_DFM if a.template == "dfm" else (PROMPT_TEMPLATE_LAB if a.template == "lab" else PROMPT_TEMPLATE)
    msgs = [{"role": "user", "content": tpl.format(question=r["Question"])}]
    enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
    ids = (enc["input_ids"] if hasattr(enc, "keys") else enc).to(dev)
    kw = {}
    if a.prefix and accepts_tt:
        kw["token_type_ids"] = torch.ones_like(ids)
    with torch.no_grad():
        gen = model.generate(ids, max_new_tokens=a.max_new, do_sample=False, pad_token_id=tok.eos_token_id, **kw)
    pred = tok.decode(gen[0][ids.shape[1]:], skip_special_tokens=True).strip().replace("\n", " ")
    rec = {"id": r["id"], "condition": "closed", "question": r["Question"], "gold": r["Answer"], "subject": r["Subject"],
           "prediction": pred, "impl": "transformers-" + str(dtype).split(".")[-1] + ("-prefix" if a.prefix else "") + f"-t{a.max_new}-{a.template}", "seconds": round(time.time() - t0, 1)}
    out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush(); n += 1
    ems.append(exact_match_score(pred, r["Answer"]))
    if n % 25 == 0: print(f"{n} rows, EM so far {sum(ems)/len(ems):.3f}, {time.time()-t0:.0f}s", flush=True)
print("done", n, "rows; EM", sum(ems) / max(1, len(ems)), flush=True)
