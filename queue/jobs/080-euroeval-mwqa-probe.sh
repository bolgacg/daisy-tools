#!/bin/bash
# EuroEval MultiWikiQA-da through our llama-server (OpenAI-compatible). Probe: 1 iteration on the test split.
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate && SERVER=~/src/llama.cpp/build/bin/llama-server
mkdir -p euroeval && cd euroeval
serve(){ $SERVER -m ~/models/$1 --port 8080 -ngl 99 -c 16384 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable --alias $2 > ../logs/server_euroeval.log 2>&1 & SPID=$!; for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done; }
stop(){ kill $SPID 2>/dev/null; wait $SPID 2>/dev/null; }
for pair in "google_gemma-3-4b-it-Q6_K.gguf gemma-3-4b-it-q6" "Qwen2.5-3B-Instruct-Q8_0.gguf qwen2.5-3b-instruct-q8"; do set -- $pair
serve $1 $2
for mid in "openai/$2" "$2"; do
  echo "=== trying model id $mid $(date +%H:%M)"
  OPENAI_API_KEY=none OPENAI_BASE_URL=http://127.0.0.1:8080/v1 timeout 14400 euroeval -m "$mid" --api-base http://127.0.0.1:8080/v1 --api-key none --dataset multi-wiki-qa-da --num-iterations 1 --evaluate-test-split --raise-errors --no-progress-bar 2>&1 | tail -25 && break
done
stop; done
ls -la; tail -5 euroeval_benchmark_results.jsonl 2>/dev/null | cut -c1-400
