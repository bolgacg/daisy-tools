#!/bin/bash
# Full 592 on the offline Danish Wikipedia index: rule query (intros), title+BM25 with composed contexts, and agentic
# (model-written query into the local index) for the 4 llama.cpp models; then the fixed Mimir through the HF server.
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate && SERVER=~/src/llama.cpp/build/bin/llama-server
serve(){ $SERVER -m ~/models/$1 --port 8080 -ngl 99 -c 12288 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/server_q.log 2>&1 & SPID=$!; for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done; }
stop(){ kill $SPID 2>/dev/null; wait $SPID 2>/dev/null; }
for pair in "gemma4b google_gemma-3-4b-it-Q6_K.gguf" "qwen3b Qwen2.5-3B-Instruct-Q8_0.gguf" "llama3b Llama-3.2-3B-Instruct-Q8_0.gguf" "llama1b Llama-3.2-1B-Instruct-Q8_0.gguf"; do set -- $pair
serve $2
for cond in retrieve retrieve-plus agentic; do
  python -m daisy_tools.runner $cond --model $1 --wiki-source local --out results/pred_$1_${cond}-local.jsonl --max-tokens 48 --parallel 3 2>&1 | tail -1
done
stop; done
python scripts/hf_server.py --port 8081 --batch 4 > logs/hf_server_local.log 2>&1 & HP=$!
for i in $(seq 1 180); do curl -s localhost:8081/health | grep -q ok && break; sleep 2; done
for cond in retrieve retrieve-plus agentic; do
  python -m daisy_tools.runner $cond --model mimir-hf --base-url http://127.0.0.1:8081/v1 --wiki-source local --out results/pred_mimir-hf_${cond}-local.jsonl --max-tokens 48 --parallel 4 2>&1 | tail -1
done
python -m daisy_tools.runner retrieve-plus --model mimir-hf --base-url http://127.0.0.1:8081/v1 --wiki-source local --queries-from results/pred_qwen3b_agentic-local.jsonl --out results/pred_mimir-hf_retrieve-plus-qwenq-local.jsonl --max-tokens 48 --parallel 4 2>&1 | tail -1
kill $HP; wait $HP 2>/dev/null
