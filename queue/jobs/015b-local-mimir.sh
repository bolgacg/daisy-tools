#!/bin/bash
# Fixed Mimir on the offline index (plain lookup, plus variant, agentic, and reading Qwen's local queries), batch 2 to fit 6 GB.
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate
sleep 5; nvidia-smi --query-gpu=memory.used --format=csv,noheader
python scripts/hf_server.py --port 8081 --batch 2 > logs/hf_server_local.log 2>&1 & HP=$!
for i in $(seq 1 180); do curl -s localhost:8081/health | grep -q ok && break; sleep 2; done; curl -s localhost:8081/health; echo
for cond in retrieve retrieve-plus agentic; do
  python -m daisy_tools.runner $cond --model mimir-hf --base-url http://127.0.0.1:8081/v1 --wiki-source local --out results/pred_mimir-hf_${cond}-local.jsonl --max-tokens 48 --parallel 2 2>&1 | grep -v "^\[" | tail -3
done
[ -s results/pred_qwen3b_agentic-local.jsonl ] && python -m daisy_tools.runner retrieve-plus --model mimir-hf --base-url http://127.0.0.1:8081/v1 --wiki-source local --queries-from results/pred_qwen3b_agentic-local.jsonl --out results/pred_mimir-hf_retrieve-plus-qwenq-local.jsonl --max-tokens 48 --parallel 2 2>&1 | grep -v "^\[" | tail -3
kill $HP; wait $HP 2>/dev/null; true
