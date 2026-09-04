#!/bin/bash
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate
python scripts/multiwikiqa.py --backend hf --model mimir-official-prefix --prefix 2>&1 | tail -2
