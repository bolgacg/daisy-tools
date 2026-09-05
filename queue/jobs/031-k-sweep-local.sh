#!/bin/bash
# 031: how many pages and how many characters one fetch should carry, Gemma 3 4B on the offline index
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate && SERVER=~/src/llama.cpp/build/bin/llama-server
$SERVER -m ~/models/google_gemma-3-4b-it-Q6_K.gguf --port 8080 -ngl 99 -c 12288 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/server_q.log 2>&1 & SPID=$!
for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done
for k in 1 5; do python -m daisy_tools.runner retrieve --model gemma4b --wiki-source local --k $k --out results/pred_gemma4b_retrieve-k$k-local.jsonl --max-tokens 64 --parallel 3 2>&1 | grep -v "^\[" | tail -2; done
python -m daisy_tools.runner retrieve --model gemma4b --wiki-source local --k 3 --chars 1800 --out results/pred_gemma4b_retrieve-c1800-local.jsonl --max-tokens 64 --parallel 3 2>&1 | grep -v "^\[" | tail -2
kill $SPID; wait $SPID 2>/dev/null; true
