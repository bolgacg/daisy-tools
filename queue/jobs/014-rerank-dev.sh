#!/bin/bash
# Paragraph reranking on the offline index, dev slice: Gemma 4B (llama.cpp) and fixed Mimir (HF server). Fast read on the idea.
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate && SERVER=~/src/llama.cpp/build/bin/llama-server
until grep -q "^done" logs/build_localwiki.log 2>/dev/null; do sleep 20; done
$SERVER -m ~/models/google_gemma-3-4b-it-Q6_K.gguf --port 8080 -ngl 99 -c 12288 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/server_q.log 2>&1 & SPID=$!
for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done
for cond in retrieve retrieve-plus; do
  python -m daisy_tools.runner $cond --data data/daisy_dev150.jsonl --model gemma4b --wiki-source local --out results/dev_gemma4b_${cond}-local.jsonl --max-tokens 48 --parallel 3 2>&1 | grep -v "^\[" | tail -4
done
python -m daisy_tools.runner retrieve-rerank --data data/daisy_dev150.jsonl --model gemma4b --wiki-source local --queries-from results/pred_qwen3b_agentic.jsonl --out results/dev_gemma4b_retrieve-rerank-qwenq-local.jsonl --max-tokens 48 --parallel 3 2>&1 | grep -v "^\[" | tail -4
kill $SPID; wait $SPID 2>/dev/null
python scripts/hf_server.py --port 8081 --batch 4 > logs/hf_server_dev.log 2>&1 & HP=$!
for i in $(seq 1 180); do curl -s localhost:8081/health | grep -q ok && break; sleep 2; done
for cond in retrieve retrieve-plus; do
  python -m daisy_tools.runner $cond --data data/daisy_dev150.jsonl --model mimir-hf --base-url http://127.0.0.1:8081/v1 --wiki-source local --out results/dev_mimir-hf_${cond}-local.jsonl --max-tokens 48 --parallel 4 2>&1 | grep -v "^\[" | tail -4
done
python -m daisy_tools.runner retrieve-rerank --data data/daisy_dev150.jsonl --model mimir-hf --base-url http://127.0.0.1:8081/v1 --wiki-source local --queries-from results/pred_qwen3b_agentic.jsonl --out results/dev_mimir-hf_retrieve-rerank-qwenq-local.jsonl --max-tokens 48 --parallel 4 2>&1 | grep -v "^\[" | tail -4
kill $HP; wait $HP 2>/dev/null
