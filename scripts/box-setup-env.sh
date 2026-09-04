#!/bin/bash
# On the box: python env for the harness and the baseline models (GGUF), sized for a 6 GB GTX 1060.
set -uo pipefail
cd ~/daisy-tools
python3 -m venv .venv && . .venv/bin/activate
pip install -q --upgrade pip && pip install -q requests pandas pyarrow nltk
python -c "import nltk, requests, pandas; print('python deps ok')"
mkdir -p ~/models && cd ~/models
dl() { # name url
  [ -s "$1" ] && { echo "have $1"; return; }
  echo "fetching $1"; curl -sSL -C - --retry 10 --retry-delay 20 -o "$1" "$2" || echo "FAILED $1"
}
dl DFM-Mimir-Q8_0.gguf                 https://huggingface.co/noctrex/DFM-Mimir/resolve/main/DFM-Mimir-Q8_0.gguf
dl Llama-3.2-3B-Instruct-Q8_0.gguf     https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q8_0.gguf
dl Llama-3.2-1B-Instruct-Q8_0.gguf     https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q8_0.gguf
dl google_gemma-3-4b-it-Q6_K.gguf      https://huggingface.co/bartowski/google_gemma-3-4b-it-GGUF/resolve/main/google_gemma-3-4b-it-Q6_K.gguf
dl Qwen2.5-3B-Instruct-Q8_0.gguf       https://huggingface.co/bartowski/Qwen2.5-3B-Instruct-GGUF/resolve/main/Qwen2.5-3B-Instruct-Q8_0.gguf
ls -la ~/models
