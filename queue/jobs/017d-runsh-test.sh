#!/bin/bash
# 017d: end-to-end test of run.sh in a fresh copy of the tree (existing index and weights reused), first 20 questions
rm -rf ~/daisy-run-test && rsync -a --exclude results --exclude .venv --exclude cache --exclude .venv-inspect ~/daisy-tools/ ~/daisy-run-test/
cd ~/daisy-run-test && LIMIT=20 LLAMA_SERVER=~/src/llama.cpp/build/bin/llama-server MODEL_GGUF=~/models/google_gemma-3-4b-it-Q6_K.gguf bash run.sh 2>&1 | grep -v "^\[" | tail -25
true
