#!/bin/bash
# On the box: for each model, serve it with llama.cpp, run the three conditions, score, report.
# Usage: scripts/run_all.sh [model-name ...]   (default: all that have a GGUF present)
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate
SERVER=~/src/llama.cpp/build/bin/llama-server
declare -A GGUF=( [mimir]=DFM-Mimir-Q8_0.gguf [llama3b]=Llama-3.2-3B-Instruct-Q8_0.gguf [llama1b]=Llama-3.2-1B-Instruct-Q8_0.gguf [gemma4b]=google_gemma-3-4b-it-Q6_K.gguf [qwen3b]=Qwen2.5-3B-Instruct-Q8_0.gguf )
ORDER=(llama1b mimir llama3b gemma4b qwen3b)
[ $# -gt 0 ] && ORDER=("$@")
mkdir -p logs results
for name in "${ORDER[@]}"; do
  f=~/models/${GGUF[$name]}
  [ -s "$f" ] || { echo "skip $name (no gguf)"; continue; }
  echo "=== $(date +%H:%M) $name"
  $SERVER -m "$f" --port 8080 -ngl 99 -c 12288 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/server_$name.log 2>&1 &
  SPID=$!
  for i in $(seq 1 90); do curl -s localhost:8080/health | grep -q '"ok"' && break; sleep 2; done
  curl -s localhost:8080/health || { echo "server for $name did not come up"; kill $SPID; continue; }
  echo
  for cond in closed retrieve agentic retrieve-oracle agentic-fewshot closed-sc; do
    python -m daisy_tools.runner $cond --model $name --out results/pred_${name}_${cond}.jsonl --max-tokens 48 --parallel 3 2>&1 | tail -2
  done
  kill $SPID; wait $SPID 2>/dev/null
done
python scripts/score.py results/pred_*.jsonl > results/scores.txt 2>&1
python scripts/report.py > results/RESULTS.md 2>&1
echo "=== $(date +%H:%M) all done"; tail -40 results/RESULTS.md
