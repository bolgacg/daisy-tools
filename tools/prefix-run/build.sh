#!/bin/bash
# Build prefix-run against an existing llama.cpp build (the fork with HrmTextForCausalLM). Usage: bash build.sh ~/src/llama.cpp
set -e
L=${1:-$HOME/src/llama.cpp}
g++ -O2 -std=c++17 -I"$L/include" -I"$L/ggml/include" -I"$L/vendor" "$(dirname "$0")/prefix-run.cpp" -o "$L/build/bin/prefix-run" -L"$L/build/bin" -lllama -lggml -lggml-base -Wl,-rpath,'$ORIGIN'
echo "built $L/build/bin/prefix-run"
