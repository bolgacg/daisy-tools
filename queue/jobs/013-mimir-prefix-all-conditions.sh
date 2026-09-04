#!/bin/bash
# Mimir through the official implementation with prefix attention, all main conditions, via the small HF server.
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate
python scripts/hf_server.py --port 8081 > logs/hf_server.log 2>&1 &
HP=$!; for i in $(seq 1 180); do curl -s localhost:8081/health | grep -q ok && break; sleep 2; done; curl -s localhost:8081/health; echo
for cond in closed retrieve retrieve-oracle agentic agentic-scaffold; do
  python -m daisy_tools.runner $cond --model mimir-hf --base-url http://127.0.0.1:8081/v1 --out results/pred_mimir-hf_$cond.jsonl --max-tokens 48 --parallel 1 2>&1 | tail -1
done
python -m daisy_tools.runner retrieve-given --model mimir-hf --base-url http://127.0.0.1:8081/v1 --queries-from results/pred_qwen3b_agentic.jsonl --out results/pred_mimir-hf_retrieve-given-qwen.jsonl --max-tokens 48 --parallel 1 2>&1 | tail -1
python -m daisy_tools.runner retrieve-given --model mimir-hf --base-url http://127.0.0.1:8081/v1 --queries-from results/pred_gemma4b_agentic.jsonl,results/pred_qwen3b_agentic.jsonl --out results/pred_mimir-hf_retrieve-given-gemma+qwen.jsonl --max-tokens 48 --parallel 1 2>&1 | tail -1
kill $HP; wait $HP 2>/dev/null
