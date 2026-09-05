"""Run the upstream DAISY task, daisy_lookup and daisy_tool on the same questions and print the scores.
Usage: OPENAI_API_KEY=none python scripts/inspect_smoke.py openai/gemma4b http://127.0.0.1:8080/v1 [limit]"""
import os, sys
os.environ.setdefault("OPENAI_API_KEY", "none")
from inspect_ai import eval as inspect_eval

model, base = sys.argv[1], sys.argv[2]
limit = int(sys.argv[3]) if len(sys.argv) > 3 else None
tasks = ["dfm_evals_task/_upstream_daisy.py@daisy", "dfm_evals_task/daisy_lookup.py@daisy_lookup", "dfm_evals_task/daisy_lookup.py@daisy_tool"]
logs = inspect_eval(tasks, model=model, model_base_url=base, limit=limit, log_dir="results/inspect", max_connections=3, display="plain")
for log in logs:
    scores = {}
    if log.results:
        for s in log.results.scores:
            scores[s.name] = {m: round(v.value, 3) for m, v in s.metrics.items()}
    print(f"{log.eval.task:14s} {log.status:9s} n={log.results.completed_samples if log.results else 0} {scores}")
