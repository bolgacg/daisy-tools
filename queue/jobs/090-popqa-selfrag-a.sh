#!/bin/bash
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate && SERVER=~/src/llama.cpp/build/bin/llama-server
serve(){ $SERVER -m ~/models/$1 --port 8080 -ngl 99 -c 16384 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/server_q.log 2>&1 & SPID=$!; for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done; }
stop(){ kill $SPID 2>/dev/null; wait $SPID 2>/dev/null; }
[ -s ~/data/selfrag/popqa_longtail.jsonl ] || curl -sSL -o ~/data/selfrag/popqa_longtail.jsonl https://huggingface.co/datasets/awinml/popqa_longtail/resolve/main/popqa_longtail.jsonl
for pair in "gemma4b google_gemma-3-4b-it-Q6_K.gguf" "qwen3b Qwen2.5-3B-Instruct-Q8_0.gguf"; do set -- $pair
serve $2
for c in closed ret5 ret10 agentic-en; do python scripts/popqa_selfrag.py $c --model $1 --parallel 3 2>&1 | tail -1; done
stop; done
