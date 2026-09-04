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
| R0 calibration: Mimir closed-book, official implementation vs paper 9.6 (same 592) | paper | 9.6 (57/592) | 8.4 (50/592) official transformers fp16, prefix attention, their prompt, 100 tokens; 5.6 on the causal-only Q8 port | CLOSED within 1 SE (1.2 pts); causal-t100 arm (012) running for the attention effect |
| R1 accuracy: best system, any small model (<=4B), model + one lookup | ours: Gemma 3 4B agentic (live API) | 40.0 | 48.2 partial (fixed Mimir, Qwen queries) | TARGET 79 = answer-recall ceiling of one lookup (Bo, 4 Sep 19:40). Report EM, ceiling, and EM/ceiling ("fraction of ceiling attained"). Realistic landing 65-72 with plain lookup on the offline index; the rest is reader fidelity |
| R2 Mimir-reader system beats every other small model's best | Gemma 40.0 | 40.0 | Mimir reads Qwen queries 38.2 (contains-gold 42.7); reads Gemma queries 36.5; rule query 26.5 | 020 done; 021 cross hybrids + query union queued |
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

- 04 Sep 14:05 job 020 done. Query generator / reader split, full 592: Mimir reads Qwen queries EM 0.382 (contains
  0.427, F1 0.446), reads Gemma queries 0.365; Qwen alone 0.400, Gemma alone 0.399. Llama 1B reads Gemma queries
  0.250 at 1.1 s/q (rule query 0.152): the cheap reader. 20 to 26 percent of model queries return nothing on Danish
  Wikipedia and fall back to the rule query; the union run (021) and English Wikipedia (040) attack that.

- 04 Sep 14:10 R0 CALIBRATED: Mimir through transformers (fp16, sdpa, token_type_ids=1 prefix attention, dfm-evals
  prompt, max 100 tokens) scores EM 0.084 (50/592) against the paper's 0.096 (57/592), one standard error apart;
  the causal-only llama.cpp Q8 port gave 0.056 (33/592). So the port cost Mimir a third of its knowledge score,
  and every Mimir tool result so far is an undercount. The official path is also faster on this card: 1.9 s per
  question against 6.0 on llama.cpp. Built scripts/hf_server.py (OpenAI-compatible, prefix attention) and queued
  job 013: all Mimir conditions rerun through it. Page and letter switch to the official Mimir numbers when 013 lands.

- 04 Sep 14:30 clean A/B on the official implementation, everything else equal: causal attention EM 0.054 (32/592),
  prefix attention 0.084 (50/592). The llama.cpp Q8 causal port gave 0.056 (33/592). So the attention mode alone
  explains the gap; 8-bit quantisation costs nothing measurable. A fact the group would want: the community GGUF
  port undercounts Mimir by about a third on knowledge QA. Job 013 (prefix Mimir, all conditions) running.

- 04 Sep 15:35 fixed Mimir (prefix attention, official path) in progress: closed 0.084 (port 0.056); retrieve with
  the rule query 0.328 on the first 341 rows (port 0.265). Expect the Qwen-query reader run to land near or above
  the 4B agentic record (0.40). Bo's 29-minute recording (English) is being transcribed on both machines.

- 04 Sep 16:45 fixed Mimir, oracle query: EM 0.698 on the first 278 rows (old port 0.606). Rule query 0.326 full.
  Transcription: large-v3 CPU pass done (285 segments); response to the recording delivered to Bo 16:40
  (lit/CONVERSATION-RESPONSE.md); GPU pass runs after job 013 as the third check.

- 04 Sep 17:40 lit-ceiling report (lit/CEILINGS-AND-READERS.md): the reader is NOT the bottleneck (our 3-4B readers
  are at ~0.86 EM when the answer is in the shown text, the human EM band); the losses are page finding (~0.5 with
  model queries) x answer-in-intro (0.79). Published passage-given EM crosses 85 only with a fine-tuned 340M+ encoder,
  a fine-tuned 7B, or an untuned 70B; Danish passage-given tops at 70.5 at any size. Verdict: 90 is not credible on any
  path (needs every stage above 0.965; above human EM). Targets: 80 realistic, 85 stretch. Paths: (a) 4B + title match
  + section rerank 60-70, +LoRA on public Danish train splits 65-75; (b) 8B Q4 reader 70-80 (75-82 with LoRA), 10-20
  s/q; (c) fine-tuned XLM-R-large extractive reader 55-70 at 0.1-0.3 s/q. Page finding by title/alias reaches 89-96% in
  the literature vs our 48-57%: that is where the headroom is. Implemented retrieve-title (exact title match on the
  offline index + section rerank); dev job 014 tests retrieve / rerank / title for Gemma 4B and fixed Mimir.
- Records: R1 target set to 80 (stretch 85) per the ceiling analysis; "90 without a bigger model" answered: no.

- 04 Sep 17:55 OFFLINE INDEX CEILING (no model, 592 q): with a local BM25 index of Danish Wikipedia (title weighted),
  the RULE query puts the subject page at rank 1 for 75.7% of questions and the answer inside the top-3 intros for
  78.0% (live Wikipedia search: 40.4%); inside the full top-3 pages 84.5%. Oracle query: 78.9 / 85.3. So the live
  search API, not the model, was the weak link: the offline index alone nearly reaches the oracle ceiling. My lexical
  paragraph rerank alone covered only 68.8%, below intros; contexts are now composed as top-page intro + best
  paragraphs (local_ceiling2 measuring). Exact title match finds the subject page first for 58.6% (any hit 87%).
  Expected: fixed Mimir with the rule query on the offline index ~0.86 x 0.78 = 65 to 68 EM, no oracle, no model
  queries. This is the "simple elegant solution": a better search index, deployable offline (nothing leaves the
  building). Dev job 014 tests it; a full-592 job follows.

- 04 Sep 18:10 composed-context ceiling (592): top-page intro + 2 best paragraphs 76.9% (below three intros, 78.0%);
  exact-title-first page finding put the subject page at rank 1 only 67.2% (BM25 rule query alone: 75.7%), so exact
  title matching is appended, not preferred. New composition "retrieve-plus": three intros + two best other
  paragraphs (target ~83%, full pages carry 84.5%). Jobs 014/015 test retrieve, retrieve-plus and agentic on the
  offline index.

- 04 Sep 18:45 dev-slice ceiling (150 q, no model): retrieve-plus (three intros + two best paragraphs, rule query,
  offline index) puts the answer in the context 82.7% of the time, above three intros (77.3%) and above the oracle-
  query intros on the full set (78.9%). This is the composition to run. Fixed Mimir: agentic 12.3% (56 calls),
  scaffold 12.3% (94 calls), oracle 69.4% final; retrieve-given-qwen running.

- 04 Sep 19:20 R2 in motion: fixed Mimir reading Qwen-written queries EM 0.482 on the first 249 rows (old port 0.382;
  Gemma alone 0.399, Qwen alone 0.400). If it holds on 592, the Mimir-reader system beats every other small model's
  own agentic result, i.e. R2 falls, still on the live Wikipedia API; the offline index run (015) comes after.

- 04 Sep 19:35 Bo's steer: MAIN PRODUCT = the model plus one Wikipedia lookup in an equal race, nothing stacked; the
  offline index is allowed as long as it cannot be called cheating or a parameter change (argument: same source, whole
  Danish Wikipedia, Nov-2023 snapshot older than the benchmark, generic BM25 with title weight, no hidden field; the
  live search box's all-words matching was the failure). Paragraph rerank / composed contexts = one labelled variant
  row, not the headline. Exact-title trick dropped from main runs. Extractive reader = later side skill. Cloud GPU: no.
  Bo found the four "new ideas from the conversation" not sharp; do not push them.

- 04 Sep 19:40 Bo: "aim for 79 and claim the theoretical limit"; "you can go on with your objectives, I trust you."
  Decomposition to report on every row: EM = answer recall (ceiling) x reader accuracy given the answer is present.
  Offline plain lookup: recall 0.78; composed variant 0.83. Reader given-present today: 0.86 (4B), Mimir-fixed ~0.87.

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
