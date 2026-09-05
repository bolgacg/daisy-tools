#!/usr/bin/env bash
# 025: PopQA long-tail (Self-RAG passages) for Llama 3.2 3B only; the 1B rows exist, Mimir on English PopQA is dropped.
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate && SERVER=~/src/llama.cpp/build/bin/llama-server
$SERVER -m ~/models/Llama-3.2-3B-Instruct-Q8_0.gguf --port 8080 -ngl 99 -c 16384 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/server_q.log 2>&1 & SPID=$!
for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done
for c in closed ret5 ret10; do python scripts/popqa_selfrag.py $c --model llama3b --parallel 3 2>&1 | tail -1; done
kill $SPID; wait $SPID 2>/dev/null; true
