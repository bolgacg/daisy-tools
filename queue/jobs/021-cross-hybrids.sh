#!/bin/bash
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate && SERVER=~/src/llama.cpp/build/bin/llama-server
serve(){ $SERVER -m ~/models/$1 --port 8080 -ngl 99 -c 12288 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/server_q.log 2>&1 & SPID=$!; for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done; }
stop(){ kill $SPID 2>/dev/null; wait $SPID 2>/dev/null; }
G=results/pred_gemma4b_agentic.jsonl; Q=results/pred_qwen3b_agentic.jsonl
serve google_gemma-3-4b-it-Q6_K.gguf
python -m daisy_tools.runner retrieve-given --model gemma4b --queries-from $Q --out results/pred_gemma4b_retrieve-given-qwen.jsonl --max-tokens 48 --parallel 3 2>&1 | grep -v "^\[" | tail -4
python -m daisy_tools.runner retrieve-given --model gemma4b --queries-from $G,$Q --out results/pred_gemma4b_retrieve-given-gemma+qwen.jsonl --max-tokens 48 --parallel 3 2>&1 | grep -v "^\[" | tail -4
stop
serve Qwen2.5-3B-Instruct-Q8_0.gguf
python -m daisy_tools.runner retrieve-given --model qwen3b --queries-from $G --out results/pred_qwen3b_retrieve-given-gemma.jsonl --max-tokens 48 --parallel 3 2>&1 | grep -v "^\[" | tail -4
python -m daisy_tools.runner retrieve-given --model qwen3b --queries-from $G,$Q --out results/pred_qwen3b_retrieve-given-gemma+qwen.jsonl --max-tokens 48 --parallel 3 2>&1 | grep -v "^\[" | tail -4
stop
serve Llama-3.2-3B-Instruct-Q8_0.gguf
python -m daisy_tools.runner retrieve-given --model llama3b --queries-from $Q --out results/pred_llama3b_retrieve-given-qwen.jsonl --max-tokens 48 --parallel 3 2>&1 | grep -v "^\[" | tail -4
stop
serve Llama-3.2-1B-Instruct-Q8_0.gguf
python -m daisy_tools.runner retrieve-given --model llama1b --queries-from $Q --out results/pred_llama1b_retrieve-given-qwen.jsonl --max-tokens 48 --parallel 3 2>&1 | grep -v "^\[" | tail -4
stop
serve DFM-Mimir-Q8_0.gguf
python -m daisy_tools.runner retrieve-given --model mimir --queries-from $G,$Q --out results/pred_mimir_retrieve-given-gemma+qwen.jsonl --max-tokens 48 --parallel 3 2>&1 | grep -v "^\[" | tail -4
stop
