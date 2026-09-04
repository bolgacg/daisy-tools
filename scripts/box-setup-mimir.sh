#!/bin/bash
# On the box: build llama.cpp from PR #27625 (HRM/Mimir support) with CUDA for the GTX 1060, fetch the Q8 GGUF.
set -euo pipefail
export PATH=/usr/local/cuda-12.8/bin:$PATH
mkdir -p ~/src ~/models && cd ~/src
if [ ! -d llama.cpp ]; then git clone -q https://github.com/ggml-org/llama.cpp.git; fi
cd llama.cpp
git fetch -q origin pull/27625/head:pr-27625
git checkout -q pr-27625
echo "llama.cpp at $(git rev-parse --short HEAD) ($(git log -1 --format=%cd --date=short))"
cmake -B build -G Ninja -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=61 -DLLAMA_CURL=ON -DCMAKE_BUILD_TYPE=Release > /tmp/cmake.log 2>&1 || { tail -30 /tmp/cmake.log; exit 1; }
cmake --build build --target llama-server llama-cli llama-bench -j4 > /tmp/build.log 2>&1 || { tail -40 /tmp/build.log; exit 1; }
echo "built: $(ls build/bin | tr '\n' ' ')"
cd ~/models
[ -f DFM-Mimir-Q8_0.gguf ] || wget -q --show-progress -O DFM-Mimir-Q8_0.gguf "https://huggingface.co/noctrex/DFM-Mimir/resolve/main/DFM-Mimir-Q8_0.gguf"
ls -la ~/models
