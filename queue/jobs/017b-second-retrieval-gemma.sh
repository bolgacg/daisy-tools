#!/bin/bash
# 017b: second-retrieval variants (labelled, Bo 5 Sep "for the heck of it"), Gemma 3 4B, full 592, offline index
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate && SERVER=~/src/llama.cpp/build/bin/llama-server
$SERVER -m ~/models/google_gemma-3-4b-it-Q6_K.gguf --port 8080 -ngl 99 -c 12288 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/server_q.log 2>&1 & SPID=$!
for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done
for c in retrieve-wide retrieve-tworound; do
python -m daisy_tools.runner $c --model gemma4b --wiki-source local --out results/pred_gemma4b_$c-local.jsonl --max-tokens 64 --parallel 3 2>&1 | grep -v "^\[" | tail -3
done
kill $SPID; wait $SPID 2>/dev/null; true
