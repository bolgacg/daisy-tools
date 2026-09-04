#!/bin/bash
# Closed-book rerun with token log-probabilities, for the confidence-gate study. Usage: run_logprobs.sh model gguf
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate
MODEL=${1:-mimir}; GGUF=${2:-DFM-Mimir-Q8_0.gguf}
~/src/llama.cpp/build/bin/llama-server -m ~/models/$GGUF --port 8080 -ngl 99 -c 12288 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/server_${MODEL}_lp.log 2>&1 &
P=$!; for i in $(seq 1 90); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done
python -m daisy_tools.runner closed --model $MODEL --out results/lp_${MODEL}_closed.jsonl --max-tokens 48 --parallel 3 --logprobs 2>&1 | tail -1
kill $P; wait $P 2>/dev/null; echo "=== lp $MODEL done $(date +%H:%M)"
