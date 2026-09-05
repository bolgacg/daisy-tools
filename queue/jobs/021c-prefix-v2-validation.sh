#!/usr/bin/env bash
# 021c: validate the redesigned prefix-LM patch (v2) on the CUDA build: DAISY closed 592 + one lookup 592.
# Server: prompt caching is disabled by the patch for prefix-LM models; --reasoning off gives the HF-default prompt
# (llama.cpp otherwise renders a <|think|> system turn); -ub 4096 so two prompts fit one ubatch (-np 2).
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate
S=~/src/llama.cpp/build-prefix/bin/llama-server
mkdir -p results/dev
$S -m ~/models/DFM-Mimir-Q8_0.gguf --alias mimir-prefix --port 8080 -ngl 99 -c 8192 -b 4096 -ub 4096 -np 2 --jinja -fa on --reasoning off > logs/server_prefix_v2.log 2>&1 & SPID=$!
for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 2; done
grep -m1 "prompt caching disabled" logs/server_prefix_v2.log || echo "WARN: no prompt-caching line in the server log (is this the v2 build?)"
T0=$(date +%s)
python -m daisy_tools.runner closed --model mimir-prefix --out results/pred_mimir-prefix_closed.jsonl --max-tokens 100 --parallel 2 2>&1 | grep -v "^\[" | tail -2
T1=$(date +%s); echo "closed wall ${T1}-${T0} = $((T1-T0)) s"
python -m daisy_tools.runner retrieve --model mimir-prefix --wiki-source local --out results/pred_mimir-prefix_retrieve-local.jsonl --max-tokens 64 --parallel 2 2>&1 | grep -v "^\[" | tail -2
T2=$(date +%s); echo "lookup wall $((T2-T1)) s"
echo "prefix-LM split warnings in server log: $(grep -c 'prefix-LM: a batch' logs/server_prefix_v2.log)"
python tools/prefix-run/compare_server.py --ref results/pred_mimir-official-prefix-t100_closed.jsonl --model mimir-prefix --n 592 --config default --out results/dev/compare592_v2.jsonl 2>&1 | grep -v Warning | tail -n 4
kill $SPID; wait $SPID 2>/dev/null; true
