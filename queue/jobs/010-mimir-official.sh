#!/bin/bash
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate
python -c "import torch, transformers; assert torch.cuda.is_available()" || { pip install -q --index-url https://download.pytorch.org/whl/cu126 torch && pip install -q transformers accelerate sentencepiece; }
python scripts/mimir_official.py --out results/pred_mimir-official_closed.jsonl
