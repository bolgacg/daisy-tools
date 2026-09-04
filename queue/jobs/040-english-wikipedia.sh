#!/bin/bash
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate && SERVER=~/src/llama.cpp/build/bin/llama-server
serve(){ $SERVER -m ~/models/$1 --port 8080 -ngl 99 -c 12288 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/server_q.log 2>&1 & SPID=$!; for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done; }
stop(){ kill $SPID 2>/dev/null; wait $SPID 2>/dev/null; }
for pair in "gemma4b google_gemma-3-4b-it-Q6_K.gguf" "llama3b Llama-3.2-3B-Instruct-Q8_0.gguf" "mimir DFM-Mimir-Q8_0.gguf"; do set -- $pair
serve $2
python -m daisy_tools.runner retrieve --model $1 --wiki-lang en --out results/pred_$1_retrieve-en.jsonl --max-tokens 48 --parallel 3 2>&1 | grep -v "^\[" | tail -4
python -m daisy_tools.runner agentic --model $1 --wiki-lang en --out results/pred_$1_agentic-en.jsonl --max-tokens 48 --parallel 3 2>&1 | grep -v "^\[" | tail -4
stop; done
