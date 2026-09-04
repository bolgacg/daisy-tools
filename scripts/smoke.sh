#!/bin/bash
# quick end-to-end check of every condition on N rows with one model
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate
MODEL=${1:-llama1b}; GGUF=${2:-Llama-3.2-1B-Instruct-Q8_0.gguf}; N=${3:-12}
mkdir -p logs results
~/src/llama.cpp/build/bin/llama-server -m ~/models/$GGUF --port 8080 -ngl 99 -c 12288 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/smoke_server.log 2>&1 &
P=$!; for i in $(seq 1 90); do curl -s localhost:8080/health | grep -q ok && break; sleep 1; done
echo "server: $(curl -s localhost:8080/health) gpu: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader)"
CONDS="closed retrieve agentic retrieve-oracle agentic-fewshot closed-sc"
for cond in $CONDS; do rm -f results/smoke_$cond.jsonl; python -m daisy_tools.runner $cond --model $MODEL --out results/smoke_$cond.jsonl --limit $N --max-tokens 48 --parallel 3 2>&1 | tail -1; done
kill $P; wait $P 2>/dev/null
python scripts/smoke_summary.py $CONDS
rm -f results/smoke_*.jsonl
