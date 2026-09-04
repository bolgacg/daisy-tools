"""Minimal OpenAI-compatible chat server over transformers, so the existing runner can drive Mimir through the
official implementation with prefix (bidirectional prompt) attention. Batched: concurrent requests are collected for
a short window and generated together (left padding), which is where the speed-up on a small GPU comes from.
Usage: python scripts/hf_server.py --port 8081 [--no-prefix] [--batch 4] [--window 0.15]"""
import argparse, json, threading, time, inspect, queue
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

ap = argparse.ArgumentParser(); ap.add_argument("--port", type=int, default=8081); ap.add_argument("--model", default="danish-foundation-models/DFM-Mimir")
ap.add_argument("--no-prefix", action="store_true"); ap.add_argument("--batch", type=int, default=4); ap.add_argument("--window", type=float, default=0.15)
a = ap.parse_args()
dev = "cuda" if torch.cuda.is_available() else "cpu"
tok = AutoTokenizer.from_pretrained(a.model); tok.padding_side = "left"
if tok.pad_token_id is None: tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.float16 if dev == "cuda" else torch.float32, attn_implementation="sdpa").to(dev).eval()
ACCEPTS_TT = "token_type_ids" in inspect.signature(model.forward).parameters
PREFIX = (not a.no_prefix) and ACCEPTS_TT
Q = queue.Queue()
print(f"hf_server: {a.model} on {dev}, prefix attention {PREFIX}, batch {a.batch}", flush=True)

def render(messages):
    enc = tok.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt", return_dict=True)
    return (enc["input_ids"] if hasattr(enc, "keys") else enc)[0]

def run_batch(items):
    # items: list of (ids_tensor, max_tokens, temperature, event_holder)
    max_new = max(it[1] for it in items); temp = items[0][2]
    L = max(int(it[0].shape[0]) for it in items)
    ids = torch.full((len(items), L), tok.pad_token_id, dtype=torch.long); attn = torch.zeros((len(items), L), dtype=torch.long)
    for i, it in enumerate(items):
        n = int(it[0].shape[0]); ids[i, L - n:] = it[0]; attn[i, L - n:] = 1
    ids, attn = ids.to(dev), attn.to(dev)
    kw = {"token_type_ids": attn.clone()} if PREFIX else {}
    if temp and temp > 0: kw.update(do_sample=True, temperature=float(temp), top_p=0.95)
    else: kw.update(do_sample=False)
    with torch.no_grad():
        g = model.generate(ids, attention_mask=attn, max_new_tokens=int(max_new), pad_token_id=tok.pad_token_id, **kw)
    for i, it in enumerate(items):
        out = g[i][L:]
        text = tok.decode(out, skip_special_tokens=True)
        it[3]["result"] = (text, int(attn[i].sum().item()), int((out != tok.pad_token_id).sum().item())); it[3]["event"].set()

def worker():
    while True:
        first = Q.get(); items = [first]; t0 = time.time()
        while len(items) < a.batch and time.time() - t0 < a.window:
            try: items.append(Q.get(timeout=a.window))
            except queue.Empty: break
        # group by temperature (sampling vs greedy) to keep generate kwargs uniform
        groups = {}
        for it in items: groups.setdefault(bool(it[2] and it[2] > 0), []).append(it)
        for grp in groups.values():
            try: run_batch(grp)
            except Exception as e:
                for it in grp: it[3]["error"] = str(e)[:300]; it[3]["event"].set()
threading.Thread(target=worker, daemon=True).start()

class H(BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def _send(self, code, obj):
        b = json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path.startswith("/health"): return self._send(200, {"status": "ok", "prefix": PREFIX, "batch": a.batch})
        self._send(404, {"error": "not found"})
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0)); body = json.loads(self.rfile.read(n) or b"{}")
        if not self.path.endswith("/chat/completions"): return self._send(404, {"error": "not found"})
        try:
            msgs = [{"role": m["role"], "content": m.get("content") or ""} for m in body.get("messages", []) if m.get("role") in ("system", "user", "assistant")]
            holder = {"event": threading.Event()}
            Q.put((render(msgs), body.get("max_tokens", 64), body.get("temperature", 0), holder))
            holder["event"].wait(timeout=600)
            if "error" in holder: return self._send(500, {"error": holder["error"]})
            text, pt, ct = holder["result"]
            self._send(200, {"id": "hf", "object": "chat.completion", "model": body.get("model", "mimir-hf"),
                             "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
                             "usage": {"prompt_tokens": pt, "completion_tokens": ct, "total_tokens": pt + ct}})
        except Exception as e:
            self._send(500, {"error": str(e)[:300]})

ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()
