#!/bin/bash
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate && SERVER=~/src/llama.cpp/build/bin/llama-server
serve(){ $SERVER -m ~/models/$1 --port 8080 -ngl 99 -c 12288 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/server_q.log 2>&1 & SPID=$!; for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done; }
stop(){ kill $SPID 2>/dev/null; wait $SPID 2>/dev/null; }
serve DFM-Mimir-Q8_0.gguf
for k in 1 5; do python -m daisy_tools.runner retrieve --model mimir --k $k --out results/pred_mimir_retrieve-k$k.jsonl --max-tokens 48 --parallel 3 2>&1 | grep -v "^\[" | tail -4; done
python -m daisy_tools.runner retrieve --model mimir --k 3 --chars 1800 --out results/pred_mimir_retrieve-c1800.jsonl --max-tokens 48 --parallel 3 2>&1 | grep -v "^\[" | tail -4
stop
