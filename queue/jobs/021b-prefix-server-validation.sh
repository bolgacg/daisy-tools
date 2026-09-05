#!/bin/bash
# 021b: the patched llama.cpp server (prefix attention for hrm-text) on the GPU: Mimir Q8 GGUF, closed book and one lookup,
# full 592, to compare answers and speed with the official transformers path (mimir-hf) and the causal port (mimir)
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate
~/src/llama.cpp/build-prefix/bin/llama-server -m ~/models/DFM-Mimir-Q8_0.gguf --alias mimir-prefix --port 8080 -ngl 99 -c 4096 -b 2048 -ub 2048 -np 1 --jinja -fa on --log-disable > logs/server_prefix.log 2>&1 & SPID=$!
for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done
python -m daisy_tools.runner closed --model mimir-prefix --out results/pred_mimir-prefix_closed.jsonl --max-tokens 100 --parallel 1 2>&1 | grep -v "^\[" | tail -2
python -m daisy_tools.runner retrieve --model mimir-prefix --wiki-source local --out results/pred_mimir-prefix_retrieve-local.jsonl --max-tokens 64 --parallel 1 2>&1 | grep -v "^\[" | tail -2
kill $SPID; wait $SPID 2>/dev/null; true
