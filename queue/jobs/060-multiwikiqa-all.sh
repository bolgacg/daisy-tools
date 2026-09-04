#!/bin/bash
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate && SERVER=~/src/llama.cpp/build/bin/llama-server
serve(){ $SERVER -m ~/models/$1 --port 8080 -ngl 99 -c 16384 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/server_q.log 2>&1 & SPID=$!; for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done; }
stop(){ kill $SPID 2>/dev/null; wait $SPID 2>/dev/null; }
pip install -q datasets 2>/dev/null
python -c "import sys; sys.path.insert(0,'.'); from scripts.multiwikiqa import load_split; print('test rows', len(load_split('test')))" || python scripts/multiwikiqa.py --limit 1 --backend server --model probe || true
for pair in "llama1b Llama-3.2-1B-Instruct-Q8_0.gguf" "llama3b Llama-3.2-3B-Instruct-Q8_0.gguf" "qwen3b Qwen2.5-3B-Instruct-Q8_0.gguf" "gemma4b google_gemma-3-4b-it-Q6_K.gguf" "mimir DFM-Mimir-Q8_0.gguf"; do set -- $pair
serve $2
python scripts/multiwikiqa.py --backend server --model $1 --parallel 3 2>&1 | tail -1
stop; done
