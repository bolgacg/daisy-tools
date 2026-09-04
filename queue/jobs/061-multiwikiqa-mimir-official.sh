#!/bin/bash
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate
python scripts/hf_server.py --port 8081 --batch 4 > logs/hf_server_mwqa.log 2>&1 &
HP=$!; for i in $(seq 1 180); do curl -s localhost:8081/health | grep -q ok && break; sleep 2; done
python scripts/multiwikiqa.py --backend server --base-url http://127.0.0.1:8081/v1 --model mimir-hf --parallel 4 2>&1 | tail -1
kill $HP; wait $HP 2>/dev/null
