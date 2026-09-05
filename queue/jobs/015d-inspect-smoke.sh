#!/bin/bash
# 015d: smoke-test the dfm-evals-format tasks (Inspect AI) on 40 questions with Gemma 3 4B, in a separate venv (Inspect needs openai>=3.1)
cd ~/daisy-tools
SERVER=~/src/llama.cpp/build/bin/llama-server
$SERVER -m ~/models/google_gemma-3-4b-it-Q6_K.gguf --alias gemma4b --port 8080 -ngl 99 -c 12288 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/server_q.log 2>&1 & SPID=$!
for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done
PYTHONPATH=~/daisy-tools OPENAI_API_KEY=none ~/inspect-venv/bin/python scripts/inspect_smoke.py openai/gemma4b http://127.0.0.1:8080/v1 40 2>&1 | grep -v "^\[" | tail -15
kill $SPID; wait $SPID 2>/dev/null; true
