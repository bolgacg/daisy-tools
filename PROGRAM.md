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
| R1 accuracy: best system, any small model (<=4B), model + one lookup | ours: Gemma 3 4B, plain lookup, offline index | 68.7 (dev 150) | full 592 running | TARGET 79 = answer-recall ceiling of one lookup (Bo, 4 Sep 19:40). Report EM, ceiling, and EM/ceiling ("fraction of ceiling attained"). Realistic landing 65-72 with plain lookup on the offline index; the rest is reader fidelity |
| R2 Mimir-reader system beats every other small model's best | OURS: fixed Mimir reads Gemma+Qwen queries (six pages) | 53.4 | 53.4 EM (contains 57.9, F1 0.596), answer-in-context 61.9%, reader fidelity 84.1%, 12.3 s/q, live API | FELL; offline-index runs next |
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

- 04 Sep 20:20 R2 FELL. Fixed Mimir (prefix attention, official path) reading Qwen-written queries: EM 0.473 on the full
  592 (contains-gold 0.503), against 0.399 / 0.400 for Gemma and Qwen doing both jobs themselves and 0.225 for the
  group's 70B from memory. Still on the live Wikipedia API. Union of Gemma + Qwen queries (two askers, six pages):
  0.618 on the first 76 rows. Offline-index runs (014 dev, 015 full) follow.

- 04 Sep 22:10 job 013 complete (its FAIL status is only the final kill/wait exit code; all seven files are full).
  Fixed Mimir reading the union of Gemma's and Qwen's queries: EM 0.534 on 592 (contains 0.579, F1 0.596); the
  answer was in the six fetched intros 61.9% of the time and the reader converted 84.1% of those. The GPU whisper job
  failed twice (CTranslate2 has no fast fp16/int8_fp16 on Pascal); the two CPU passes agree at 96% and suffice, so it
  is dropped. Dev job 014 (offline index) running.

- 04 Sep 22:40 FIRST OFFLINE-INDEX READER RESULTS (dev slice, 150 q, Gemma 3 4B): plain one-lookup (rule query, three
  intros) EM 0.687 (contains 0.727), answer-in-context 0.780, reader fidelity 0.846, 5.7 s/q; retrieve-plus 0.713
  (ans-in-ctx 0.827); rerank with Qwen queries 0.640. Same 150 questions on the live API: retrieve 0.307, agentic
  0.347, oracle 0.727. So the plain lookup on the offline index (0.687) sits one point under the oracle query (0.727)
  and 38 points above the same lookup through the live search box. Fraction of ceiling attained: 0.687/0.780 = 88%.
  Full run (015) in progress; Mimir-hf part failed on CUDA OOM (batch 4 with long contexts): 015b queued with batch 2.

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

## 2026-09-05 00:35 FULL-SET OFFLINE-INDEX RESULTS (job 015, gemma4b + qwen3b landed; llama3b/1b pending; Mimir-hf in 015b)
Gemma 3 4B, 592, their prompt and scorer. closed 5.6 | live search box rule query 31.1 | live agentic 39.9 |
oracle query (live) 67.9 | OFFLINE INDEX plain lookup 65.7 EM (contains 69.3; answer in 3 intros 75.5%; fidelity 85.5%;
fraction of intro ceiling 87%; 5.6 s/q; 944 prompt tok) | retrieve-plus-local 68.8 (variant) | agentic-local 48.5.
Qwen2.5 3B: closed 3.0 | live 27.9 / agentic 40.0 | local plain 59.8 | local plus 63.9 | local agentic 56.0 (529/592).
Findings: (1) main-line full-set number is 65.7, two points under the live oracle ceiling; dev slice (68.7) was 3 points
optimistic, inside its CI. (2) On the BM25 index the whole question as query beats a model-written query for both
models (65.7 vs 48.5; 59.8 vs 56.0): the query generator is a cost, not a gain, once the engine ranks properly.
(3) Target R1=79 not reached; the gap is 24.5% of questions whose answer is not in the three intros plus 14.5%
reading loss. One lookup of three intros cannot reach 79; the paragraphs variant reaches 68.8. Recommend to Bo: quote
65.7 (87% of ceiling) as the main line and present the ceiling decomposition, not chase 79 with stacked steps.
R1 holder: Gemma 3 4B plain lookup offline index 65.7 (full 592). Next: 015 remainder, 015b Mimir-hf local.

## 2026-09-05 01:45 job 015 finished (FAIL status = expected Mimir-hf OOM at batch 4; all llama.cpp parts complete)
Full 592, offline index, plain lookup EM (intro recall 75.5% for all; fidelity in brackets):
gemma4b 65.7 (85.5) | llama3b 61.3 (79.4) | qwen3b 59.8 (77.6) | llama1b 33.8 (44.5). Plus-paragraphs variant:
68.8 / 64.4 / 63.9 / 41.2. Agentic (model writes query) on offline index: gemma 48.5, qwen 55.4, llama3b 3.7,
llama1b 0.7 (the Llamas never emit the SEARCH line; unchanged from live). Reading fidelity separates the readers
cleanly: 85 > 79 > 78 > 45 with identical retrieved text. 015b (Mimir-hf, batch 2) started 01:41.

## 2026-09-05 02:20 dfm-evals-format task written (dfm_evals_task/daisy_lookup.py): daisy_lookup (main line) and daisy_tool
(native tool decision), upstream scorer/prompt vendored, imports and builds on the box; the lookup returns the same titles
as the runner for the first question. Smoke job 015c (40 q, Gemma, closed vs lookup vs tool) queued after 015b.
Mimir-hf on the offline index, first 134 rows: EM 67.9, fidelity 85.6, Gemma on the same ids 67.2 (NOT a record until 592).
Letter and CV still cite the live-API numbers ("40 percent", "factor of five"); update once Mimir lands, in one pass.

## 2026-09-05 02:55 where the plain lookup's misses go (full 592, top-3 pages for the question itself)
Answer in the 3 intros 75.5% | in a top-3 page but below the intro 9.1% | not in the top-3 pages 15.4% (of these, 28 questions
= 4.7% sit in ranks 4 to 10; 63 = 10.6% are not in the top 10 at all). So the intro-only fetch caps at 75.5, whole pages at 84.6,
and 79 (Bo's target) needs the paragraphs variant or a second fetch. Queue changes: 021 cross-hybrids and 030 k-sweep (live API,
causal Mimir) dropped as superseded; 016 native tools switched to the offline index; 031 k-sweep-local (Gemma, k=1/5, chars 1800) added.
Mimir-hf offline interim 311 rows: 63.3 vs Gemma 62.1 on the same ids.

## 2026-09-05 04:05 RECORD: Mimir (official, prefix) with one plain lookup on the offline index, full 592: EM 65.9
(contains 70.3, fidelity 86.1%, 26 s/q on Pascal fp16, 944 prompt tokens). Gemma 3 4B same condition 65.7. The 1B Danish model
reads as well as the 4B; both sit 2 points under the live oracle ceiling (67.9 / 69.4) and at 87% of the intro ceiling (75.5).
R1 holder: Mimir-hf 65.9 = Gemma 65.7 (tie within noise). R2 (Mimir best) moved 53.4 -> 65.9, now a single model with one lookup.
Page rewritten in the answer-bo voice: three acts (ruler / one lookup, two engines / decision), run-it-yourself coda with the
dfm-evals task, model card with cost columns; headless walk clean at 1536 and 390 (0 errors, 0 overflow, 0 empty fills).
Letter and CV still to update (they cite 40 percent and factor of five).

## 2026-09-05 07:30 Mimir-hf paragraphs variant (retrieve-plus-local, labelled, NOT main line), full 592: EM 71.6
(contains 75.7; answer in context 81.2%; fidelity 87.1%; 43 s/q). Gemma same variant 68.8. Job 015b now runs Mimir agentic-local
(expected: never searches), then the superseded qwenq condition, which the skip watcher (~/queue/skip-qwenq.sh) kills on start.
Headline stays the main line: Mimir 65.9 / Gemma 65.7 with one plain lookup.

## 2026-09-05 08:15 job 015b DONE. Mimir-hf agentic-local (writes its own search line, offline index): EM 12.0, searched 56 of 592.
Confirms: Mimir does not act as a tool user without training; as a reader it is the best small model. The qwenq condition was
killed on start by the skip watcher (superseded). 015c Inspect smoke test running.

## 2026-09-05 08:25 015c smoke test failed in 18 s: Inspect needs openai>=3.1, the daisy venv pins 2.54 (litellm). Fix: separate
~/inspect-venv on the box (inspect-ai 0.3.263, openai 3.8.0), task import-checked there; 015d re-queued after 016 (native tools, local).

## 2026-09-05 09:05 job 016 native tool calls (OpenAI tools API through each chat template), offline index, full 592
gemma4b: 0 calls, EM 5.6 (Gemma 3 has no native tool format in llama.cpp) | qwen3b: 144 calls (24%), EM 16.9 | mimir port: 0 calls, 3.2 |
llama3b: called on 143/143 then the run died on a llama.cpp parse error ("does not match the expected peg-native format").
Runner patched to log tool_format_error rows and continue; 016b resumes llama3b after the smoke test.
Reading: the native tool channel does not create judgement either; Qwen's 24% of calls score far below the plain lookup (16.9 vs 59.8).

## 2026-09-05 09:10 Inspect (dfm-evals format) smoke test PASSED, Gemma 3 4B, first 40 questions
upstream daisy 0.050 | daisy_lookup 0.600 | daisy_tool 0.050 (Gemma never calls the tool natively). Our runner on the same 40 ids:
closed 0.050, retrieve-local 0.600: identical. 015e queued: both tasks on all 592 (the official-format number for the page coda).

## 2026-09-05 09:20 016b done. Llama 3.2 3B, native tool call, offline index, full 592: EM 52.5, called on 589/592 (3 parse errors).
Finding for act three: the same Llama 3B never searched when told in text (3.7, 0 calls) and always searches when the tool is offered
in its native format (52.5, 100% calls). Whether a small model "decides" to search is set by the interface, not by what it knows.
Its own tool queries still lose to the plain question (52.5 vs 61.3). 015e (Inspect full 592, Gemma) running.

## 2026-09-05 09:45 015e DONE: their Inspect format, all 592, Gemma 3 4B: daisy 5.4 (se 0.9) | daisy_lookup 66.0 (se 1.9), f1 0.705.
Harness: 5.6 / 65.7. The two paths agree within half a point; the page coda now states this check. Queue: 017 PopQA long-tail (a) running.

## 2026-09-05 10:30 R6 PopQA long-tail (Self-RAG's 1,399 questions and passages, contains-gold), Gemma 3 4B: closed 19.0 | top-5 passages 55.4
Published on the same set: Self-RAG 7B 54.9, 13B 55.8 (trained); Llama2-7B + retrieval 38.2; ChatGPT + retrieval 50.8. An untrained 4B
reader at 55.4 is level with the trained Self-RAG rows. ret10 and the agentic-en condition still running (job 017), then 023 for Qwen.

## 2026-09-05 12:10 Bo's six points (5 Sep morning) acted on
1. Second retrieval "for the heck of it", labelled: two new runner conditions, retrieve-wide (10 pages, 3 intros + 4 best paragraphs,
   rule based) and retrieve-tworound (model writes one follow-up query when the text lacks the answer); job 017b, Gemma, full 592.
2. Query writing was never part of the test: benchmark has no tool; on the ranked index the query was the whole question 592/592
   (search box: rule shortened 199/592). Stated on the page.
3. Page section "Questions asked along the way": his six questions in order, answer-bo voice; tour step 8; walk clean.
4. Dev-slice numbers acceptable when labelled (memory feedback_demo_follows_bos_questions).
5. One-click: run.sh (venv, index, weights, server, both Inspect tasks, table; INSPECT_MODEL=hf/vllm path for clusters),
   colab/daisy_lookup_colab.ipynb (untested until public), README; 017c tests run.sh end to end on the box (LIMIT=20).
   Their usual UI is `inspect view`; run.sh prints the command.
6. Recommendations status: dfm-evals task DONE and verified (66.0 vs 65.7); Mimir in the reader seat DONE (65.9);
   public issue on the attention finding DRAFTED (lit/ISSUE-DRAFT-mimir-prefix-attention.md), waits for Bo's text approval.

## 2026-09-05 12:35 R6 PopQA long-tail interim (contains-gold, 1,399 q, Self-RAG passages): gemma4b closed 19.0 | ret5 55.4 | ret10 54.9 |
agentic-en 32.8; qwen3b closed 21.4 | ret5 54.0 (ret10, agentic-en running). Published: Self-RAG 7B 54.9 / 13B 55.8; Llama2-7B+ret 38.2;
ChatGPT+ret 50.8. Both untrained small readers land on the trained Self-RAG rows. Page field section to get this table when 017 closes.

## 2026-09-05 13:10 R6 CLOSED (job 017): PopQA long-tail, Self-RAG passages, contains-gold, 1,399 q
gemma4b: closed 19.0 | top5 55.4 | top10 54.9 | own query on live English Wikipedia 32.8 (always searched)
qwen3b:  closed 21.4 | top5 54.0 | top10 55.6 | own query 31.9 (searched 1396/1399)
Self-RAG paper Table 2: Llama2-7B 14.7 -> 38.2; Llama2-13B 14.7 -> 45.7; Self-RAG 7B 54.9; 13B 55.8. Untrained 3B/4B readers on
identical passages match the trained 7B/13B rows. On the page: field section table + text. 017b (second retrieval, Gemma) running.

## 2026-09-05 13:50 PUBLISHED on Bo's greenlight ("greenlight for all things you wanna do", "gimme the demo link")
github.com/bolgacg/daisy-tools (public, branch master, MIT, README, SDU-Daisy as submodule pointer), GitHub Pages from gh-pages
(site/ contents + .nojekyll): https://bolgacg.github.io/daisy-tools/ serving 200. History checked: no Claude trailers.
From now on the cycle pushes master after each commit (git log check first) and republishes gh-pages when site/ changes.
Box gene unreachable since about 13:20 (Tailscale timeout; tether). Queue runs on locally (017b second retrieval was running).
Bo's new asks (13:30): score decomposition bar (charity-dollar pattern), real-life relevance write-up, intuitive-design skill
(written: ~/.claude/skills/intuitive-design/), issue text to show before filing.

## 2026-09-05 14:35 page pass on Bo's asks: light mode only (page.css overrides the dark tokens), copy cut by about a third,
prompt in a collapsible, "Where the 592 questions go" two-row segmented chart with ceiling ticks (3 intros / whole pages / top 10;
1 intro and +paragraphs ticks appear when 031 lands), generated sentences shortened to the two-numbers rule, tour step 6 now the
chart. Walk clean; master pushed; gh-pages republished via scripts/publish_pages.sh; live check 200, 0 errors.
Box still unreachable after the power loss (14:35); Bo asked to reconnect the phone.

## 2026-09-05 18:05 POWER-CUT INCIDENT closed (13:20 to 18:03, about 4 h 40 min of GPU lost)
Chain: mains cut -> box off (BIOS "Restore AC Power Loss" default = stay off) -> flat CMOS cell wiped BIOS -> cold start halted
at the "press F1" prompt (Q-code d7, no keyboard attached, no picture on the TV until a reset) -> Secure Boot came back on
with the CMOS defaults -> the DKMS-signed NVIDIA module was refused ("Key was rejected by service") -> the requeued job ran
on CPU until I stopped the queue. MOK enrolment via mokutil staged four times; the MokManager screen timed out each time.
Fix applied by Bo in the BIOS (18:00): Secure Boot OS Type = Other OS (driver loads), Wait For F1 If Error = Disabled,
Boot Option 1 = Ubuntu (P1 Kingston), Restore AC Power Loss = Power On. Driver back (nvidia-smi OK), queue re-enabled,
017b requeued from row 461 (460 rows salvaged, 0 corrupt). Root cause still open: the CMOS battery (CR2032) must be replaced
or every cold start repeats this. Tether watchdog fired at boot as designed; adb devices empty -> investigate (setFunctions
rndis drops the adb function; should be rndis,adb).

## 2026-09-05 18:20 Bo approved ("do it"): comment posted as bolgacg on ggml-org/llama.cpp PR #27625 (noctrex, HrmTextForCausalLM),
text identical to the draft shown to Bo: https://github.com/ggml-org/llama.cpp/pull/27625#issuecomment-5553071594
Follow-up questions there are Bo's to answer; check the thread once a day until the deadline.

## 2026-09-05 18:35 job 017b DONE: second-retrieval variants, Gemma 3 4B, full 592, offline index (labelled, not main line)
plain lookup 65.7 (ceiling 75.5, fidelity 85.5, 944 tok) | +2 paragraphs same pages 68.8 (81.2, 83.2, 1302 tok) |
wide: 10 pages, 3 intros + 4 best paragraphs 67.2 (81.6, 81.0, 1340 tok) | two-round: model writes a follow-up query when
the text lacks the answer 64.4 (76.4, 82.7, 1068 tok; asked 100 times).
Reading: a second retrieval buys almost nothing here. The wider net lifts the ceiling by 0.4 points over the paragraphs
variant and costs 2 points of fidelity (more text, more distraction). Letting the model decide on a second query lowers
the score: it asks only 100 times and the extra instruction costs 3 points of reading fidelity on every question.
Best labelled variant stays "+paragraphs" (Gemma 68.8, Mimir 71.6). Page q_second fill now shows all three. 017c (run.sh test) running.

## 2026-09-05 19:05 GitHub/HF sweep (lit/GITHUB-WEB.md, 9.8k words) changes three things
1. Their harness attends bidirectionally on both serving paths (vLLM hrm_text.py PrefillPrefixLMAttention; native engine
   prefixlm mask). Our 8.4 vs 5.4 is a statement about the community port, not about their numbers. Page and comment are correct.
2. Two DAISY task definitions exist: upstream dfm-evals `daisy` (README prompt, 100 tokens, ASCII normaliser) and the lab fork
   `sdu-daisy` (dfm7.py: "Besvar spørgsmålet kort og præcist på dansk.", 64 tokens, lowercase+whitespace exact). The published
   9.6 is not tied to either in public code. Action: run the fork protocol on Mimir prefix (job 017e) and report both; page
   note added to act one.
3. Dataset audit: 13 answer-in-question leaks, 2 "Ukendt" golds, 1 hint question, 2 unmatched list golds, 98 golds with Danish
   letters the official normaliser deletes, count inconsistency 746/741/740/592. Candidate for a friendly SDU-Daisy issue (Bo's call).
Also: Peter Schneider-Kamp is peter-sk on GitHub/HF and said (HF, 20 Aug) "we will happily provide GGUFs once this is sorted";
PR 27625 has zero reviews; noctrex is a GGUF hobbyist; quantised Mimir cards (3 Sep) report Daisy 8.8 (FP8) and 7.6 (AWQ).
Decisions for Bo: ask Jacob/Peter which protocol produced 9.6; open three one-line dfm-evals PRs (CODEOWNERS, suite, authors).

## 2026-09-05 20:10 R5 their reading task (dfm-evals multi_wiki_qa, Danish, 2,048 rows, their protocol, EM / F1)
llama1b 2.8 / 25.3 (does not obey "max 3 words") | llama3b 42.5 / 65.9 | gemma4b 45.6 / 72.7 | qwen3b 53.6 / 71.9.
Their Table: Mimir 66.8; Qwen 3.5 4B 57.1; Gemma 4 E2B 44.1; Gemma 3 1B 42.6. Mimir official on 512 rows queued (022).

## 2026-09-05 20:15 017d run.sh end-to-end test PASSED in a fresh copy (~/daisy-run-test, existing index and weights, LIMIT=20):
venv created, deps installed (incl. openai), server started, upstream daisy + daisy_lookup + daisy_tool ran, table printed,
"inspect view" hint shown. The one-command path is real. Benchmark-noise table live on the page (leak 11, unknown 2, multi 2,
no question mark 1, Danish letters in gold 98) with a browser filter and per-question flags. 017e (Mimir, lab protocol) running.

## 2026-09-05 21:10 017e: Mimir under the lab fork's DAISY protocol (dfm7.py sdu-daisy: short prompt, 64 tokens), prefix attention, 592
lab exact (lowercase, whitespace) 1.0 | ascii EM 1.0 | gold contained in the prediction 11.1 | mean answer length 9.9 words.
Mimir answers the short prompt in full sentences, so exact match under that protocol is near 1 percent; the published 9.6
cannot come from it. The library protocol (README prompt with "kun det direkte svar", 100 tokens) is the one that lands near
9.6 (ours 8.4, SE 1.2). Calibration question closed without emailing. Causal variant of the lab run still finishing (259/592).

## 2026-09-05 22:45 prefix-LM fix for the llama.cpp port (Bo: build it, then offer it; no asking)
George (noctrex) replied 19:54: limitation known, prefix mode "a much larger change ... later". Our comment had not credited
his limitations note (partial whoops; recovery = the patch). Built tonight:
1. tools/prefix-run/prefix-run.cpp: driver using the public llama_set_causal_attn API (off for the prompt batch, on for
   generation). No llama.cpp change. Smoke on 3 questions (CPU): identical answers to the official transformers prefix path,
   different from the causal port. Full 592 closed-book running on CPU (GPU busy with 022), both modes, resume-by-id.
2. tools/prefix-run/patch/apply_prefixlm.py + 0001 patch: 15-line in-tree change in llama_context::decode (multi-token
   ubatch = prompt, causal off; single-token = generation, causal on; warning if the prompt exceeds n_ubatch). Applied on
   the box tree; CPU-only build in ~/src/llama.cpp/build-cpu running. Branch hrm-text-prefix-lm on top of noctrex's
   hrm-text-support in a local shallow clone, committed as Bo; fork bolgacg/llama.cpp exists; push after validation.
Also today: PRs opened on Bo's approval: dfm-evals #8 (CODEOWNERS), SDU-Daisy #2 (scorer fixes + tests). Four demo repos
rewritten to describe themselves without addressee lines. GitHub profile: name/bio pending the device flow (code issued twice).
