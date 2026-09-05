# What one Wikipedia lookup does to DAISY

DAISY is the Odense NLP group's quiz on the Danish Culture Canon. It measures what a language model remembers.
This repository gives the same models one lookup in Danish Wikipedia and measures three separate skills instead:
finding the page, reading it, and knowing when to look. Everything is the group's own: their questions, their
prompt, their scorer, their model. Results page: https://bolgacg.github.io/daisy-tools/

| Exact match on the 592 public questions | From memory | One lookup, ranked index |
|---|---|---|
| DFM Mimir 1B (official implementation, prefix attention) | 8.4 | 65.9 |
| Gemma 3 4B | 5.6 | 65.7 |
| Llama 3.2 3B | 4.1 | 61.3 |
| Qwen 2.5 3B | 3.0 | 59.8 |
| Llama 3.2 1B | 0.8 | 33.8 |

The lookup sends the question, as written, to a BM25 index over the full Danish Wikipedia dump of 1 November 2023
and puts the introductions of the top three pages in front of the group's prompt. The answer was in that text for
75.5 percent of questions; Mimir converts 86 percent of those. No model here decides when to look: told it may
search, each either always searched or never did, and Mimir claims to know the answer on 84 percent of the
questions it then gets wrong. One side finding: the community llama.cpp port reads Mimir's prompt with causal
attention only, which costs a third of its score from memory (5.6 against 8.4 on the official code path).

## Run it

```
bash run.sh              # environment, index (about 20 minutes the first time), weights, model server, both tasks, the table
LIMIT=40 bash run.sh     # two-minute check
.venv-inspect/bin/inspect view --log-dir results/inspect     # every question, fetched text, answer and score
```

`dfm_evals_task/` holds the tasks in the dfm-evals (Inspect AI) format: `daisy_lookup` (one lookup, the question as
the query) and `daisy_tool` (the same search offered as a tool call; the model decides). `daisy_tools/runner.py` is
the harness behind every row on the page, with more conditions (search-box lookup, oracle query, self-consistency,
free-form and native tool calls, labelled second-retrieval variants). `scripts/` builds the index, the report and
the page data. `results/` holds every logged answer. `PROGRAM.md` is the working log.

## Credits and licences

Benchmark and prompt: [SDU-Daisy](https://github.com/schneiderkamplab/SDU-Daisy) (MIT), vendored as a submodule,
paper arXiv 2601.19930. Model: [DFM Mimir](https://huggingface.co/danish-foundation-models/DFM-Mimir), report arXiv
2608.13517. `dfm_evals_task/_upstream_daisy.py` is the DAISY task file from
[dfm-evals](https://github.com/danish-foundation-models/dfm-evals), reproduced unchanged so the scorer is theirs;
see that repository for its terms. Wikipedia text: Wikimedia dump 20231101.da via Hugging Face `wikimedia/wikipedia`
(CC BY-SA 4.0). Everything else in this repository: MIT, Bolgaç Gülen, 2026.
