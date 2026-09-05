#!/usr/bin/env bash
# One command: environment, Danish Wikipedia index, model server, the DAISY tasks in the dfm-evals (Inspect AI) format, the table.
#   bash run.sh                      full 592 questions, Gemma 3 4B through llama-server on one consumer GPU
#   LIMIT=40 bash run.sh             quick check on the first 40 questions
#   INSPECT_MODEL=hf/google/gemma-3-4b-it bash run.sh      use Inspect's own model providers (hf, vllm, openai) instead of llama-server
# Afterwards: .venv-inspect/bin/inspect view --log-dir results/inspect   opens every question, fetched text, answer and score in the browser.
set -euo pipefail
cd "$(dirname "$0")"
INDEX=${DAWIKI_DB:-$HOME/data/dawiki/dawiki.sqlite}
MODEL_GGUF=${MODEL_GGUF:-models/google_gemma-3-4b-it-Q6_K.gguf}
MODEL_URL=${MODEL_URL:-https://huggingface.co/bartowski/google_gemma-3-4b-it-GGUF/resolve/main/google_gemma-3-4b-it-Q6_K.gguf}
PORT=${PORT:-8080}
LIM=${LIMIT:+--limit $LIMIT}

[ -d .venv-inspect ] || python3 -m venv .venv-inspect
.venv-inspect/bin/pip install -q --upgrade pip
.venv-inspect/bin/pip install -q inspect-ai datasets requests pyarrow

if [ ! -f "$INDEX" ]; then
  echo "== building the Danish Wikipedia index at $INDEX (dump of 1 Nov 2023, about 20 minutes, 0.9 GB)"
  DAWIKI_DB="$INDEX" .venv-inspect/bin/python scripts/build_localwiki.py
  DAWIKI_DB="$INDEX" .venv-inspect/bin/python scripts/build_title_index.py
fi

if [ -z "${INSPECT_MODEL:-}" ]; then
  SERVER=${LLAMA_SERVER:-$(command -v llama-server || true)}
  if [ -z "$SERVER" ] || [ ! -x "$SERVER" ]; then
    echo "llama-server not found. Build llama.cpp (cmake -B build -DGGML_CUDA=ON && cmake --build build -j) and set LLAMA_SERVER=/path/to/llama-server,"
    echo "or run with INSPECT_MODEL=hf/google/gemma-3-4b-it (transformers) or INSPECT_MODEL=vllm/google/gemma-3-4b-it."; exit 1
  fi
  if [ ! -f "$MODEL_GGUF" ]; then mkdir -p "$(dirname "$MODEL_GGUF")"; echo "== downloading the model weights"; curl -L -o "$MODEL_GGUF" "$MODEL_URL"; fi
  "$SERVER" -m "$MODEL_GGUF" --alias model --port "$PORT" -ngl 99 -c 12288 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > /tmp/daisy-llama-server.log 2>&1 &
  SPID=$!; trap 'kill $SPID 2>/dev/null || true' EXIT
  for i in $(seq 1 120); do curl -s "localhost:$PORT/health" | grep -q ok && break; sleep 2; done
  INSPECT_MODEL="openai/model"; export OPENAI_API_KEY=none; BASE="--model-base-url http://127.0.0.1:$PORT/v1"
else
  BASE=""
fi

export PYTHONPATH=.
echo "== their DAISY task (from memory)"
.venv-inspect/bin/inspect eval dfm_evals_task/_upstream_daisy.py@daisy --model "$INSPECT_MODEL" $BASE --log-dir results/inspect --display plain $LIM
echo "== DAISY with one lookup, and with the lookup offered as a tool"
.venv-inspect/bin/inspect eval dfm_evals_task/daisy_lookup.py@daisy_lookup dfm_evals_task/daisy_lookup.py@daisy_tool --model "$INSPECT_MODEL" $BASE -T index_path="$INDEX" --log-dir results/inspect --display plain $LIM
echo
echo "Done. Open the runs: .venv-inspect/bin/inspect view --log-dir results/inspect"
