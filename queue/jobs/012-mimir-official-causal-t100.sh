#!/bin/bash
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate
python scripts/mimir_official.py --max-new 100
