#!/usr/bin/env bash
# 028: the upstream dfm-evals `daisy` task (the exact library code behind the published number) with Mimir
# served through the patched llama.cpp port. Last replication path for the published 9.6 our hardware can run.
set -uo pipefail
cd ~/daisy-tools
~/src/llama.cpp/build-prefix/bin/llama-server -m ~/models/DFM-Mimir-Q8_0.gguf --alias mimir-prefix --port 8080 -ngl 99 -c 4096 -b 2048 -ub 2048 -np 1 --jinja -fa on --reasoning off > logs/server_prefix_daisy028.log 2>&1 & SPID=$!
for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done
source ~/inspect-venv/bin/activate
cd ~/dfm-evals-test && mkdir -p logs
T0=$(date +%s)
OPENAI_API_KEY=none PYTHONPATH=. inspect eval dfm_evals/tasks/daisy.py@daisy \
  --model openai/mimir-prefix --model-base-url http://127.0.0.1:8080/v1 --max-connections 2 --log-dir logs/inspect-daisy-mimir --log-format json 2>&1 | tail -n 6
echo "wall $(( $(date +%s) - T0 )) s; split warnings: $(grep -c 'prefix-LM: a batch' ~/daisy-tools/logs/server_prefix_daisy028.log)"
python - <<'PY'
import json, glob
f = sorted(glob.glob("logs/inspect-daisy-mimir/*.json"))[-1]; d = json.load(open(f))
for s in d["results"]["scores"]:
    print("028 upstream daisy task, Mimir via patched port, n", d["results"].get("total_samples"), s["name"], round(100*s["metrics"]["mean"]["value"],1), "se", round(100*s["metrics"]["stderr"]["value"],1))
PY
kill $SPID; wait $SPID 2>/dev/null; true
