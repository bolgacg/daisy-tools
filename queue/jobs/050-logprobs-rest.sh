#!/bin/bash
set -uo pipefail
cd ~/daisy-tools && bash scripts/run_logprobs.sh llama1b Llama-3.2-1B-Instruct-Q8_0.gguf && bash scripts/run_logprobs.sh qwen3b Qwen2.5-3B-Instruct-Q8_0.gguf
