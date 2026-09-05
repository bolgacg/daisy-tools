# DAISY with one lookup, in the dfm-evals format

Two Inspect AI tasks that keep everything from `dfm_evals.tasks.daisy` (dataset, prompt, greedy decoding,
100 tokens, the ASCII exact-match scorer) and add one thing: a lookup in Danish Wikipedia before the answer.

| task | what the model gets |
|---|---|
| `daisy_lookup` | the introductions of the top three pages for the question itself, then their prompt |
| `daisy_tool` | the same search offered as a tool call; the model may answer without searching |

The index is a BM25 index (SQLite FTS5, title weighted 10) over the full Danish Wikipedia dump of
1 November 2023, older than the benchmark. No field of the benchmark other than the question is used.

## Run

```
pip install inspect-ai datasets
python scripts/build_localwiki.py            # about 20 minutes, writes ~/data/dawiki/dawiki.sqlite (0.9 GB)
OPENAI_API_KEY=none inspect eval dfm_evals_task/daisy_lookup.py@daisy_lookup \
    --model openai/<served model name> --model-base-url http://127.0.0.1:8080/v1
```

Any OpenAI-compatible server works (llama-server, vLLM). Task arguments: `-T index_path=... -T k=3 -T chars=900`.
`scripts/inspect_smoke.py <model> <base_url> [limit]` runs closed book, lookup and tool on the same questions
and prints the three scores.
