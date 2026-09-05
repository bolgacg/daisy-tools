#!/bin/bash
# 016b: resume Llama 3.2 3B native tool calls on the offline index (016 died at row 143 on a llama.cpp tool-call parse error; runner now logs and continues)
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate && SERVER=~/src/llama.cpp/build/bin/llama-server
$SERVER -m ~/models/Llama-3.2-3B-Instruct-Q8_0.gguf --port 8080 -ngl 99 -c 12288 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/server_q.log 2>&1 & SPID=$!
for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done
python -m daisy_tools.runner agentic-native --model llama3b --wiki-source local --out results/pred_llama3b_agentic-native-local.jsonl --max-tokens 64 --parallel 3 2>&1 | grep -v "^\[" | tail -3
kill $SPID; wait $SPID 2>/dev/null; true
