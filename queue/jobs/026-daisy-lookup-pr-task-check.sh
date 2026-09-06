#!/usr/bin/env bash
# 026: run the dfm-evals pull-request version of daisy_lookup (dfm_evals/tasks/daisy_lookup.py in ~/dfm-evals-test)
# against the real offline index with Gemma 3 4B, all 592 questions, and print exact match next to the harness number (65.7).
set -uo pipefail
cd ~/daisy-tools && SERVER=~/src/llama.cpp/build/bin/llama-server
$SERVER -m ~/models/google_gemma-3-4b-it-Q6_K.gguf --alias gemma4b --port 8080 -ngl 99 -c 12288 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/server_q.log 2>&1 & SPID=$!
for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done
source ~/inspect-venv/bin/activate
cd ~/dfm-evals-test && mkdir -p logs
T0=$(date +%s)
OPENAI_API_KEY=none PYTHONPATH=. inspect eval dfm_evals/tasks/daisy_lookup.py@daisy_lookup -T index_path=/home/bo/data/dawiki/dawiki.sqlite \
  --model openai/gemma4b --model-base-url http://127.0.0.1:8080/v1 --max-connections 3 --log-dir logs/inspect-daisy-lookup --log-format json 2>&1 | tail -n 12
echo "wall $(( $(date +%s) - T0 )) s"
python - <<'PY'
import json, glob
f = sorted(glob.glob("logs/inspect-daisy-lookup/*.json"))[-1]
d = json.load(open(f))
for s in d["results"]["scores"]:
    print("PR task daisy_lookup, n", d["results"].get("total_samples"), s["name"], round(100*s["metrics"]["mean"]["value"],1), "se", round(100*s["metrics"]["stderr"]["value"],1))
PY
kill $SPID; wait $SPID 2>/dev/null; true
