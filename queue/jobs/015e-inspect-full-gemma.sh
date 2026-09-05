#!/bin/bash
# 015e: the dfm-evals-format tasks on all 592 with Gemma 3 4B: upstream daisy and daisy_lookup (the official-format numbers for the page)
cd ~/daisy-tools
SERVER=~/src/llama.cpp/build/bin/llama-server
$SERVER -m ~/models/google_gemma-3-4b-it-Q6_K.gguf --alias gemma4b --port 8080 -ngl 99 -c 12288 -np 3 -ctk q8_0 -ctv q8_0 --jinja -fa on --log-disable > logs/server_q.log 2>&1 & SPID=$!
for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done
PYTHONPATH=~/daisy-tools OPENAI_API_KEY=none ~/inspect-venv/bin/python - <<'PY' 2>&1 | grep -v "^\[" | tail -6
import os
from inspect_ai import eval as ev
logs = ev(["dfm_evals_task/_upstream_daisy.py@daisy", "dfm_evals_task/daisy_lookup.py@daisy_lookup"], model="openai/gemma4b", model_base_url="http://127.0.0.1:8080/v1", log_dir="results/inspect", max_connections=3, display="plain")
import json
out = {}
for log in logs:
    sc = {s.name: {m: v.value for m, v in s.metrics.items()} for s in (log.results.scores if log.results else [])}
    out[log.eval.task] = {"status": log.status, "n": log.results.completed_samples if log.results else 0, "scores": sc}
    print(log.eval.task, log.status, out[log.eval.task]["n"], sc)
json.dump(out, open("results/inspect_full_gemma4b.json", "w"), indent=1)
PY
kill $SPID; wait $SPID 2>/dev/null; true
