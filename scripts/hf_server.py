"""Minimal OpenAI-compatible chat server over transformers, so the existing runner can drive Mimir through the
official implementation with prefix (bidirectional prompt) attention. Sequential, greedy, fp16 on the GPU.
Usage: python scripts/hf_server.py --port 8081 [--no-prefix]"""
import argparse, json, threading, time, inspect
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

ap = argparse.ArgumentParser(); ap.add_argument("--port", type=int, default=8081); ap.add_argument("--model", default="danish-foundation-models/DFM-Mimir")
ap.add_argument("--no-prefix", action="store_true"); a = ap.parse_args()
dev = "cuda" if torch.cuda.is_available() else "cpu"
tok = AutoTokenizer.from_pretrained(a.model)
model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.float16 if dev == "cuda" else torch.float32, attn_implementation="sdpa").to(dev).eval()
ACCEPTS_TT = "token_type_ids" in inspect.signature(model.forward).parameters
PREFIX = (not a.no_prefix) and ACCEPTS_TT
LOCK = threading.Lock()
print(f"hf_server: {a.model} on {dev}, prefix attention {PREFIX}", flush=True)

def generate(messages, max_tokens, temperature):
    enc = tok.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt", return_dict=True)
    ids = (enc["input_ids"] if hasattr(enc, "keys") else enc).to(dev)
    kw = {"token_type_ids": torch.ones_like(ids)} if PREFIX else {}
    if temperature and temperature > 0:
        kw.update(do_sample=True, temperature=float(temperature), top_p=0.95)
    else:
        kw.update(do_sample=False)
    with LOCK, torch.no_grad():
        g = model.generate(ids, max_new_tokens=int(max_tokens), pad_token_id=tok.eos_token_id, **kw)
    out = g[0][ids.shape[1]:]
    return tok.decode(out, skip_special_tokens=True), int(ids.shape[1]), int(out.shape[0])

class H(BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def _send(self, code, obj):
        b = json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path.startswith("/health"): return self._send(200, {"status": "ok", "prefix": PREFIX})
        self._send(404, {"error": "not found"})
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0)); body = json.loads(self.rfile.read(n) or b"{}")
        if not self.path.endswith("/chat/completions"): return self._send(404, {"error": "not found"})
        try:
            msgs = [{"role": m["role"], "content": m.get("content") or ""} for m in body.get("messages", []) if m.get("role") in ("system", "user", "assistant")]
            text, pt, ct = generate(msgs, body.get("max_tokens", 64), body.get("temperature", 0))
            self._send(200, {"id": "hf", "object": "chat.completion", "model": body.get("model", "mimir-hf"),
                             "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
                             "usage": {"prompt_tokens": pt, "completion_tokens": ct, "total_tokens": pt + ct}})
        except Exception as e:
            self._send(500, {"error": str(e)[:300]})

ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()
