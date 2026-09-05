"""Write the exact templated prompt token ids the official transformers path uses, so the llama.cpp driver reads
the same tokens. Usage: python make_prompts.py data/daisy.jsonl out.jsonl [--template dfm|lab]"""
import json, sys
from transformers import AutoTokenizer
sys.path.insert(0, ".")
from daisy_tools.metrics import PROMPT_TEMPLATE_DFM
src, out = sys.argv[1], sys.argv[2]
tok = AutoTokenizer.from_pretrained("danish-foundation-models/DFM-Mimir")
with open(out, "w") as fh:
    for l in open(src):
        r = json.loads(l)
        msgs = [{"role": "user", "content": PROMPT_TEMPLATE_DFM.format(question=r["Question"])}]
        ids = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=True)
        if hasattr(ids, "input_ids"): ids = ids["input_ids"]
        fh.write(json.dumps({"id": r["id"], "gold": r["Answer"], "ids": list(map(int, ids))}) + "\n")
print("wrote", out)
