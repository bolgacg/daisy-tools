#!/usr/bin/env bash
# 022b: Mimir on their reading benchmark (dfm-evals multi_wiki_qa protocol, 512 rows) through the v2 prefix-LM server.
# Replaces 022 (transformers path, about 5 h); labelled "patched port" on the page. Their published Mimir row: 66.8 EM.
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate
S=~/src/llama.cpp/build-prefix/bin/llama-server
$S -m ~/models/DFM-Mimir-Q8_0.gguf --alias mimir-prefix --port 8080 -ngl 99 -c 8192 -b 4096 -ub 4096 -np 2 --jinja -fa on --reasoning off > logs/server_prefix_mwqa.log 2>&1 & SPID=$!
for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done
T0=$(date +%s)
python scripts/multiwikiqa.py --backend server --base-url http://127.0.0.1:8080/v1 --model mimir-prefix --parallel 2 --limit 512 2>&1 | tail -2
echo "mwqa wall $(( $(date +%s) - T0 )) s; split warnings: $(grep -c 'prefix-LM: a batch' logs/server_prefix_mwqa.log)"
kill $SPID; wait $SPID 2>/dev/null; true
