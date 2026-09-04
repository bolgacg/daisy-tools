# PROGRAM.md: the autonomous improvement cycle (started 4 Sep 2026 12:45). Read this first on every wake-up.

## Mission (Bo, 4 Sep): "aim for the moon; fully autonomous improvement cycle until we get there; if we get
## there, beat it by more, more efficiently, in all avenues at once; total dominance."
Field: the Odense NLP group's DAISY benchmark (592 public questions), their prompt, their scorer, plus the cost
axis. Standing rules: compute and paper need no permission; NOTHING outward (publish, email, message a real
person) without Bo's explicit OK; commits as Bo, no trailers; no em dashes anywhere; application deadline
Sun 7 Sep 23:59 stays on track in parallel (letter/CV/bundle exist in sdu-applications/submission/4203).

## The records (all on the 592, exact match by their script unless stated)
| record | holder now | value | our best | status |
|---|---|---|---|---|
| R0 calibration: Mimir closed-book, official implementation vs paper 9.6 (same 592) | paper | 9.6 | 5.6 (Q8 llama.cpp, causal) | jobs 011/012 (prefix A/B) pending |
| R1 accuracy: best system, any small model (<=4B) | ours: Gemma 3 4B agentic | 40.0 | 40.0 | beaten 70B closed (22.5); next target 50 |
| R2 Mimir-reader system beats every other small model's best | Gemma 40.0 | 40.0 | Mimir reads Gemma queries 36.5; reads Qwen queries 40.0 (105 rows, running) | job 020 running; 021 cross hybrids + query union queued |
| R3 cost: EM per second per question, EM per 1k tokens (Pareto) | Gemma agentic 40.0 @ 5.9 s | | build the frontier | needs cost table |
| R4 decision quality: selective prediction (coverage vs risk), AUROC of confidence | Mimir AUROC 0.91 (sum logprob) | | gate useless on DAISY (base rate 5%) | second benchmark needed |
| R6 identical-terms record: PopQA long-tail 1,399 with Self-RAG's released passages, acc(contains) | untrained Llama2-7B+ret 38.2, Alpaca-7B 46.7, Llama2-chat-13B 51.8, Ret-ChatGPT 50.8; trained Self-RAG 7B 54.9, CRAG 59.8 | 51.8 (untrained) | not run | data download + runner needed |
| R7 identical-terms record: EuroEval MultiWikiQA-da (2048 q, 4-shot, F1/EM) via the CLI on our llama-server | Mimir 79.94/66.25; Llama-3.2-3B-Inst 70.23/52.62; Llama-3.3-70B 70.18/41.74; board best 83.76/69.88 | | not run (Gemma 3 4B and Qwen 2.5 3B are holes on the board) | euroeval install + backend check |
| R5 second field: Multi Wiki QA da, their task code verbatim | their paper: Mimir 66.8, Gemma 3 1B 42.6 | 66.8 | not run | jobs 060/061 queued |

## Findings so far (keep appending, dated)
- 04 Sep 12:33 confidence gate: token log-probabilities predict closed-book correctness well (AUROC sum-logprob
  Mimir 0.906, Llama3B 0.893, Gemma 0.834) but with 4 to 6 percent base rate a gate saves almost no lookups
  without losing accuracy (Mimir: 7.6% answered from memory costs 1.5 points). Conclusion: the gate is a cost
  tool for benchmarks where memory is worth something; on DAISY always-retrieve is optimal. R4 moves to R5.

- 04 Sep 13:05 lit-metrics report landed (lit/METRICS-AND-TERMS.md): canonical names applied to page and report
  (EM = SQuAD EM; lenient = contains-gold accuracy as in PopQA/Self-RAG; ceiling = answer recall@3 / DPR top-k
  retrieval accuracy; query quality = page-level R-precision; fidelity = reader accuracy given retrieval success
  + distraction rate; 2x2 = retrieval-necessity confusion matrix; coverage/selective risk; "oracle query" never
  "gold passage"; agentic = single-round tool decision). Closest comparable: Search-R1 Qwen2.5-3B PopQA 10.8 /
  38.7 / 43.5 (direct / RAG / trained) vs ours on DAISY contains-gold 4.1 / 31.6 / 44.6 untrained. No published
  Danish RAG number exists: our tables are the first (say so). Page got a "How this sits in the field" section.

- 04 Sep 13:20 lit-group report (lit/GROUP-PAPERS.md): their Daisy 9.6 was measured on the SAME 592 rows (57
  correct vs our 33; SE 1.2 points, so the gap is real). Their harness: Inspect via dfm-evals, greedy, max_tokens
  100, one user message, chat template, ASCII normaliser (we vendored it). Mechanism candidates: Mimir is a
  prefix-LM and the llama.cpp port is causal-only (PR says so; 95.8% top-1 agreement at q8); transformers applies
  bidirectional prompt attention only with token_type_ids=1; our q8 KV cache; GGUF template. A/B queued (011
  prefix, 012 causal, both their template and 100 tokens). Hidden apples: Multi Wiki QA da (Mimir 66.8 EM, Gemma 3
  1B 42.6; task code fetched to lit/dfm-evals and replicated in scripts/multiwikiqa.py; jobs 060/061 queued);
  PIQA-da, DaLA, GEC-DaLA, bfcl-v1-da. Native tool interface: Mimir's chat template renders Gemma-4 tool
  definitions and 9.46% of its post-training data is agentic; job 015 offers the search tool natively. Their
  conventions we now add: stderr/CI (bootstrap CI added to the report), calibration metrics, latency definition.
  Feasible learned decision: SFT Gemma 3 270M on <tool_call>search_web(...)</tool_call> rows (their BADM500 repo).
  Job 010 failed (BatchEncoding bug), fixed; 011/012 carry the calibration.

- 04 Sep 13:35 R2 MOVED: query generator / reader split. Mimir reading Gemma-written queries: EM 0.365 (rule query
  0.265; Gemma itself 0.399); reading Qwen-written queries 0.400 on the first 105 rows. The query is the lever and
  Mimir reads as well as the 3-4B models once the page is right. Cost: Mimir 9.1 s/q as reader plus ~1 s asker; not
  cheaper than Gemma alone (5.9 s). Next: cross hybrids and union of two askers' queries (job 021).

- 04 Sep 13:40 lit-sota report (lit/SOTA-COMPARABLES.md): our numbers land where the literature predicts (closed-book
  = long-tail floor; +15 to +28 points from one lookup is the field's band; untrained 3-4B agentic at 40 EM equals
  RL-trained 3B search agents on English single-hop sets because RL barely beats one-call RAG there). Two runs on
  identical terms recommended: PopQA long-tail with Self-RAG's released passages (beat untrained 7B/13B rows with a
  4B: the English twin of the DAISY story) and EuroEval MultiWikiQA-da for Gemma 3 4B and Qwen 2.5 3B (board holes;
  a 3-4B above Llama-3.3-70B's 41.74 EM is the norm there). Added as R6 and R7.

- 04 Sep 14:00 queue now holds 12 jobs: 011/012 prefix A/B, 015 native tools, 021 cross hybrids + query union,
  030 k sweep, 040 English Wikipedia, 050 logprobs rest, 060/061 Multi Wiki QA (their task verbatim), 080 EuroEval
  MultiWikiQA-da probe (1 iteration; model id syntax to confirm), 090/091 PopQA long-tail on Self-RAG's released
  passages (HF mirror awinml/popqa_longtail: 1,399 rows, 20 passages each; metric match). The Self-RAG Google Drive
  link is dead (404), the mirror carries the same fields. Estimated queue time: 20 to 30 hours on the 1060.

## Backlog (ranked; pick the top feasible on each wake-up; mark done/failed with the number)
1. R0: read job 010 result; if official Mimir >> 5.6, switch Mimir runs to transformers path (or fix Q8/PR).
2. R2: hybrids (job 020): Gemma-asks/Mimir-reads, Qwen-asks/Mimir-reads. Then a cheaper asker: the rule query
   improved with the model's own reformulation (one short call) and a "best of both" (try own query, fall back).
3. R1: push the asker: few-shot query examples, two-round search, k=5 with reranking by title match, entity
   extraction before search, English+Danish Wikipedia union (job 040 gives the English half).
4. R1: reader improvements: answer-type hints (year/name), strict format post-processing (lenient->exact gain),
   snippet windowing around the query terms instead of intros.
5. R3: cost table for every condition (tokens in, tokens out, calls, seconds); Pareto plot on the page.
6. R5: run WikiQA-DA (or ScandiQA-da) closed-book for Mimir with their settings to calibrate, then the gate.
7. Page: canonical metric names from lit/METRICS-AND-TERMS.md, cost axis, comparables section, updated verdicts.
8. Letter/CV: refresh numbers whenever a record moves; keep to one page and two pages.
9. Nicer: question browser diffing two systems; per-subject leaderboard; failure taxonomy with counts.

## Cycle on every wake-up
1. `bash ~/queue/qstatus.sh` over ssh; read new lit/*.md from agents; rsync results back.
2. Rebuild RESULTS.md and site/data.js; run scripts/confidence_gate.py and any new analysis.
3. Update the records table and findings above; decide the next 1 to 3 experiments; write them as queue
   jobs (queue/jobs/NNN-name.sh, copy to gene:~/queue/pending); code changes rsynced first.
4. Commit locally as Bo. If a record moved or something broke, tell Bo in one short message; else stay quiet.
