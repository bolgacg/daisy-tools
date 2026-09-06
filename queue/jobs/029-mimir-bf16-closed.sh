#!/usr/bin/env bash
# 029: Mimir closed-book via transformers in bfloat16 (precision variant of the 8.4 fp16 reference), full 592.
set -uo pipefail
cd ~/daisy-tools && . .venv/bin/activate
python scripts/mimir_official.py --prefix --max-new 100 --dtype bfloat16 --out results/pred_mimir-official-prefix-bf16-t100_closed.jsonl 2>&1 | tail -n 3
python - <<'PY'
import json
from daisy_tools.metrics import exact_match_score as em
rows=[json.loads(l) for l in open("results/pred_mimir-official-prefix-bf16-t100_closed.jsonl")]
print("029 bf16 prefix closed: n", len(rows), "EM", round(100*sum(em(r["prediction"] or "", r["gold"]) for r in rows)/len(rows),1))
PY
