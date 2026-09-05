#!/bin/bash
# 017e: Mimir (official, prefix attention) under the lab fork's DAISY protocol (dfm7.py sdu-daisy: short prompt, 64 tokens),
# to see which of the group's two task definitions reproduces the published 9.6
cd ~/daisy-tools && . .venv/bin/activate
python scripts/mimir_official.py --prefix --max-new 64 --template lab 2>&1 | grep -v "^\[" | tail -3
python scripts/mimir_official.py --max-new 64 --template lab 2>&1 | grep -v "^\[" | tail -3
true
