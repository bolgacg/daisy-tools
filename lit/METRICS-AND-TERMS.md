# Metrics and terms for the DAISY tool study

Written 4 Sep 2026 for the daisy-tools results page and the 4203 letter. Every number below was read
from the cited paper on 4 Sep 2026 (arXiv abstract or full text, model cards where stated). Where a
number is quoted from a figure rather than a table, the entry says so. Our own numbers are in
results/RESULTS.md and are not repeated here except where a comparison needs them.

Contents

1. The compression analogy
2. Mapping table: our name, canonical term, definition, citation, reporting convention
3. Standard names for our conditions and roles
4. Recommended metric set and names for the page and the letter
5. Comparables: closest published results, with numbers
6. Pitfalls

Notation used throughout: EM = exact match; acc(contains) = the gold string appears inside the
prediction; k = number of retrieved passages; RC = retriever calls per question; "PopQA" = Mallen et
al. 2023, 14k questions; "NQ" = Natural Questions open; "TQA" = TriviaQA.


## 1. The compression analogy

Data compression has a settled vocabulary that maps cleanly onto what this study measures.

- Entropy H (Shannon 1948, "A mathematical theory of communication"): the floor on bits per symbol
  for lossless coding of a source. Language-model papers report the same quantity as
  bits per byte (bpb) or bits per character, and as perplexity = 2^(bits per token). RETRO
  (arXiv 2112.04426) reports its headline result on the Pile in bits per byte, so the bridge is
  literal inside the retrieval literature.
- Compression ratio: uncompressed size divided by compressed size. Space saving is 1 minus its
  inverse.
- Rate R: bits spent per symbol. Distortion D: expected loss between source and reconstruction under
  a distortion measure, typically mean squared error (MSE) or Hamming distance.
- Rate-distortion function R(D) (Shannon 1959, "Coding theorems for a discrete source with a
  fidelity criterion"): the minimum rate that achieves distortion at most D. Plotted, it is the
  rate-distortion curve; any real coder sits on or above it. The trade-off is the whole subject.
- Lossless versus lossy: lossless coding has D = 0 and R >= H; lossy coding spends fewer bits than
  H and pays in distortion.
- Fidelity metrics for lossy images: PSNR in decibels, computed from MSE against the original, and
  SSIM (Wang, Bovik, Sheikh, Simoncelli 2004, IEEE Trans. Image Processing 13(4)), a structural
  similarity index in [0, 1]. Both are "distortion" measured in a perceptual currency.
- Side information (Wyner and Ziv 1976, IEEE Trans. Information Theory 22(1)): bits available to the
  decoder that were not sent by the encoder. Retrieval is side information at the decoder.
- Systems metrics: throughput (bytes per second), latency (time to code one block), memory (working
  set, dictionary or window size).

How the study reads in that vocabulary. The model's parameters are a lossy compression of the
Danish canon; closed-book EM is one minus the distortion of that codebook on 592 probes. Retrieval
hands the decoder (the reader) side information at decode time. Tokens per question is the rate.
The plot of EM against tokens per question, one point per condition, is the rate-distortion curve
of the whole system, and the always-retrieve point and the never-retrieve point are its two corners.
The retrieval ceiling is the distortion floor for a given side channel (the top three intros): no
reader can do better than the answers it was handed. Reading fidelity is decoder fidelity given
side information. The decision to search is a rate-allocation decision made per symbol. EM is the
lossless criterion (the string must match); F1, BLEU and contains-match are lossy criteria that pay
partial credit. Use the analogy once, in the primer, and then use the canonical names below.


## 2. Mapping table

The table gives the short form; the numbered entries after it give the reporting conventions and
the pitfalls for each row.

| Our name | Canonical term(s) | Definition | Defining or popularising papers | How leading papers report it |
|---|---|---|---|---|
| EM (strict) | Exact match (EM) | 1 if the normalised prediction equals a normalised gold answer, else 0; normalisation = lowercase, strip punctuation and articles, collapse whitespace | SQuAD, Rajpurkar et al. 2016, arXiv 1606.05250; DAISY eval.py uses the same normalisation | Percent or fraction; "EM" column; open-domain QA tables (REALM, RAG, DPR, RETRO, Atlas) all use EM |
| Lenient EM | Accuracy, contains-match; also "acc", "In-Accuracy", "cover-EM" | 1 if any gold answer string is a substring of the normalised prediction | Mallen et al. 2023, arXiv 2212.10511 ("correct if any substring of the prediction is an exact match of any of the gold answers"); Self-RAG, arXiv 2310.11511 ("whether gold answers are included in the model generations"); Adaptive-RAG, arXiv 2403.14403 ("Acc"); Moskvoretskii et al. 2025, arXiv 2501.12835 ("In-Accuracy") | Reported as "accuracy" or "acc" next to EM and F1; Toolformer (arXiv 2302.04761) uses "first 20 words contain the correct answer" |
| Token F1 | F1 (SQuAD F1, word-level F1) | Harmonic mean of precision and recall over the bag of normalised tokens shared between prediction and gold; max over gold answers | Rajpurkar et al. 2016, arXiv 1606.05250 | Percent, "F1" column beside EM |
| BLEU | Sentence-level BLEU with smoothing | Geometric mean of modified n-gram precisions (n = 1..4) times a brevity penalty; smoothing method 4 of Chen and Cherry 2014 (WMT) as in NLTK sentence_bleu | Papineni et al. 2002 (ACL); Chen and Cherry 2014, "A systematic comparison of smoothing techniques for sentence-level BLEU" | Rare in QA; the DAISY paper (arXiv 2601.19930) reports BLEU and F1, no EM |
| closed | Closed-book QA; "No Retrieval"; "Never RAG"; "Direct inference"; "vanilla LM" | The model answers from parameters only | Roberts, Raffel, Shazeer 2020, arXiv 2002.08910 (coined closed-book); Jeong 2024 ("No Retrieval"); Moskvoretskii 2025 ("Never RAG"); Search-R1, arXiv 2503.09516 ("Direct inference") | EM, and in newer papers acc(contains) |
| retrieve | Retrieve-then-read; single-step retrieval; always-retrieve; standard RAG (with a rule-based query rewriter) | Retrieve top-k passages for a query derived from the question, then read | Chen et al. 2017 DrQA, arXiv 1704.00051 (retriever + reader); Lewis et al. 2020, arXiv 2005.11401 (RAG); Ma et al. 2023, arXiv 2305.14283 ("retrieve-then-read" vs "rewrite-retrieve-read") | EM at fixed k; k is stated (DPR k = 100 for the reader, RAG k in {5, 10}, Self-RAG k = 5, Search-R1 k = 3, Atlas k = 20 to 40) |
| retrieve-oracle | Oracle query (gold-entity query); not the same as "gold passage" or "oracle context" | The retriever is given the benchmark's Subject field as the query; the reader still sees k = 3 intros | Nearest: KILT provenance page, Petroni et al. 2021, arXiv 2009.02252; "oracle" in Liu et al. 2023, arXiv 2307.03172, means the gold document alone | Report as an upper bound on query formulation, in the same EM column, labelled oracle |
| agentic | Adaptive retrieval (self-decided); on-demand retrieval; single-action ReAct; function calling with relevance detection | The model may emit one search action or answer directly; one round | Mallen 2023 (adaptive retrieval, popularity rule); Self-RAG 2023 (Retrieve token); ReAct, Yao et al. 2022, arXiv 2210.03629 (search[entity]); BFCL (ICML 2025, PMLR v267) "relevance detection" = withhold the call when no function fits; Labruna et al. 2024, arXiv 2404.19705 (Adapt-LLM, RET token) | EM or acc plus the retrieval rate (share of questions with a call); Jeong reports Step and Time; Moskvoretskii reports RC and LMC |
| agentic-fewshot | Same with in-context demonstrations | As above, with worked examples in the prompt | Toolformer and ReAct use few-shot exemplars for the action format | Same columns; state the shot count |
| agentic-scaffold | Decide-then-retrieve; priori judgement; self-knowledge by direct prompting | Step 1: "Do you know the answer with certainty, yes or no"; step 2: search on no | Ren et al. 2023, arXiv 2307.11019 ("priori judgement", give-up rate); Wang et al. 2023 SKR, arXiv 2310.05002 ("direct prompting" for self-knowledge); Kadavath et al. 2022, arXiv 2207.05221 (P(IK)) | Accuracy plus give-up rate and the accuracy of the judgement (Ren: Eval-Acc) |
| closed-sc | Self-consistency; majority vote over samples; a test-time scaling method | Sample n answers at temperature > 0, return the most frequent | Wang et al. 2022, arXiv 2203.11171; Snell et al. 2024, arXiv 2408.03314 (compute-optimal test-time scaling) | EM against n samples; report n and temperature |
| confidence gating (logprobs) | Uncertainty-based adaptive retrieval; selective prediction with MaxProb; token-probability trigger | Compute a confidence score from the closed-book answer's token log-probabilities; search (or abstain) when the score is below a threshold | FLARE, Jiang et al. 2023, arXiv 2305.06983 (retrieve if any token prob < theta); Kamath et al. 2020, arXiv 2006.09462 (MaxProb selective QA); Moskvoretskii 2025 (27 uncertainty estimators as retrieval gates); TARG, arXiv 2511.09803 (prefix entropy, top-1/top-2 margin) | Risk-coverage curve, AUROC, retrieval rate at each threshold |
| retrieval ceiling | Top-k retrieval accuracy; answer recall@k; hit rate; "Hit"; answer coverage | Share of questions for which at least one of the top-k passages contains a gold answer string | Karpukhin et al. 2020 DPR, arXiv 2004.04906 (top-k retrieval accuracy); Ma et al. 2023 ("Hit = 1 if answer in doc"); KILT Recall@k is page-level (provenance), not string-level | "Top-20 / Top-100" columns in DPR (NQ: BM25 59.1 / 73.7, DPR 78.4 / 85.4); k stated |
| reading fidelity | Reader accuracy conditioned on retrieval success; context utilization; EM given answer present | EM restricted to questions where a gold string is inside the retrieved text; its complement (EM given absent) is the parametric residual | No single defining paper; nearest: DPR reader given gold passage; Liu et al. 2023 oracle condition; "Can Small Language Models Use What They Retrieve?", arXiv 2603.11513 ("retrieval utilization", oracle EM on Known / Unknown splits, "distraction effect") | Conditional EM with n; 2603.11513 reports oracle EM split by whether the closed-book answer was right |
| 2x2 (called when wrong, silent when wrong, called when right, silent when right) | Retrieval-necessity confusion matrix; selective prediction (coverage and selective risk); self-knowledge accuracy | Cross-tabulate the search decision with closed-book correctness; positives = retrieval needed (closed-book wrong) | Geifman and El-Yaniv 2017, arXiv 1705.08500 (coverage, selective risk); Ren 2023 (give-up rate, Right/G); Yin et al. 2023 SelfAware, arXiv 2305.18153 (self-knowledge F1); Whitehead et al. 2022, arXiv 2204.13631 (effective reliability) | Coverage and risk pairs, or the curve; abstention literature reports C@R (coverage at fixed risk) and AUC |
| call precision, call recall | Precision and recall of the "need retrieval" decision | precision = called when wrong / all calls; recall = called when wrong / all closed-book wrong | Same as the row above; SKR and Adapt-LLM evaluate the decision only through end accuracy | Report beside the always-call baseline (precision = closed-book error rate, recall = 1) |
| query quality (first hit = subject page) | Precision@1 on the provenance page; page-level R-precision with one gold page; Hit@1 | 1 if the first search result is the question's subject page | KILT, arXiv 2009.02252 (R-precision r/R over provenance pages; with R = 1 it is P@1); MRR and nDCG for ranked lists (Voorhees 1999; Jarvelin and Kekalainen 2002) | R-precision and Recall@5 columns in KILT; state the retriever (Wikipedia opensearch) |
| tokens per question | Tokens per query; inference cost; prompt tokens and generated tokens | Mean prompt and completion tokens per question, per condition | Self-Route, arXiv 2407.16833 (cost = tokens as a share of the long-context baseline); Jeong 2024 (Time relative to single-step); Snell 2024 (accuracy vs test-time compute) | Absolute tokens or relative cost, plus the accuracy-vs-cost plot (Pareto frontier) |
| seconds per question | Latency (wall-clock per query); throughput = questions per second | Mean seconds per question on stated hardware | Jeong 2024 (Time); TARG (seconds per query); Mallen 2023 (inference time and API cost) | With hardware, batch size, quantisation, context length |
| tool calls per question | Retriever calls (RC); retrieval rate; retrieval frequency; number of retrievals (#Num) | Mean number of search calls per question (0 or 1 in our design, so equal to the retrieval rate) | Moskvoretskii 2025 (RC, LMC); DRAGIN, arXiv 2403.10081 (#Num); FLARE (share of sentences that trigger); Adapt-LLM (retrieval rate) | RC column beside accuracy |
| fallback (empty result) | Retrieval failure; empty retrieval | The model's query returned no page; the harness fell back | No canonical term; Search-R1 counts invalid searches | Count and share |
| default-answer collapse | Degenerate or repeated predictions; mode collapse of the answer distribution | Share of rows covered by the most frequent predictions | No canonical QA term; "mode collapse" is the generative-model term | Top repeated strings with counts |
| by answer type (year, number, text) | Answer-type breakdown | EM per answer class | SQuAD and NQ papers break down by answer type; PopQA by relation | Per-class EM with n |
| replication | Re-scoring of published predictions; reproduction | The group's five prediction files scored with their script on the 592 public golds | No canonical term; "reproduction" in ML reproducibility papers | Side by side with the paper's numbers |
| failure taxonomy | Error analysis; error categories | Rule-labelled classes of wrong answers with counts | Standard practice (SQuAD, DrQA, Kamalloo et al. 2023, arXiv 2305.06984) | Table of categories with counts and examples |

### 2.1 Exact match

Definition (SQuAD, arXiv 1606.05250): a prediction is correct if, after normalisation, it equals
any of the gold answers. The DAISY script applies the same normalisation (case, punctuation,
articles, whitespace) and the benchmark has a single gold per question. Open-domain QA tables from
REALM (arXiv 2002.08909) onwards report EM as a percent with one decimal; RETRO, Atlas, DPR and FiD
do the same. Pitfalls: EM under-counts correct answers that differ in surface form. Roberts et al.
2020 hand-checked 150 NQ predictions marked wrong and found 62% were true positives. Kamalloo et
al. 2023 (arXiv 2305.06984) found EM 12.6 versus human-judged 71.4 for zero-shot InstructGPT on
NQ-open, because long generations do not match. Short-answer prompts (ours) shrink that gap but do
not close it; the 13 near-misses like "Forlaget Gyldendal" are the residual.

### 2.2 Contains-match accuracy

Mallen et al. 2023 define correctness as "any substring of the prediction is an exact match of any
of the gold answers"; Self-RAG, Adaptive-RAG ("Acc"), Rewrite-Retrieve-Read and Moskvoretskii et
al. 2025 ("In-Accuracy") use the same test, and Toolformer tests the first 20 words. When a paper
in the adaptive-retrieval line says "accuracy", assume this metric unless it says EM. Pitfall: it
inflates with output length (a long answer that lists several candidates is scored correct) and it
over-scores years and small numbers, which appear inside unrelated text. Always report it beside
strict EM and keep the answer length short.

### 2.3 Token F1

SQuAD F1 over normalised tokens, maximum over gold answers. Reported beside EM in every reading
comprehension and open-domain QA paper. On one-word answers F1 equals EM; the gap between them
is the share of partial matches ("Niels W. Gade" against "Gade").

### 2.4 BLEU on short answers

BLEU (Papineni et al. 2002) is a corpus-level metric for translation. The DAISY script computes
sentence-level BLEU per answer with NLTK's method 4 smoothing (Chen and Cherry 2014): for a
hypothesis shorter than four tokens the higher-order precisions are undefined and are replaced by
smoothed counts that shrink with the hypothesis length. On one- to three-word answers BLEU is
therefore a re-scaled unigram precision with a length penalty, and it is not comparable across
systems that produce different answer lengths. Report it only because it is the benchmark's own
number, in the replication table, with a footnote.

### 2.5 Retrieval ceiling

DPR (arXiv 2004.04906) defines top-k retrieval accuracy as the fraction of questions for which at
least one of the top-k passages contains a span that answers the question, and reports it as
"Top-20" and "Top-100" columns (NQ: BM25 59.1 and 73.7, DPR 78.4 and 85.4). Ma et al. 2023 call the
same quantity "Hit". Other names in use: answer recall@k, hit rate@k, answer coverage. KILT's
Recall@k is a different thing (page-level provenance), so do not borrow that name. Our three
ceilings (question 0.215, shaped 0.404, subject 0.787 at k = 3, intros only) are top-3 answer recall
under three query formulations. Pitfalls: the string test has both error directions (a year can be
present for another reason; an answer can be inferable but not literal), and the ceiling is a
property of the snippet policy (lead sections, 3 pages) as much as of the corpus.

### 2.6 Reading fidelity

There is no single canonical name. The nearest established quantities are (a) reader accuracy
given the gold passage (DPR's reader on gold contexts; Liu et al. 2023's "oracle" setting, where
gpt-3.5-turbo scores 88.3 with only the answer document against 56.1 closed-book), and (b) the 2026
paper "Can Small Language Models Use What They Retrieve?" (arXiv 2603.11513), which calls it
retrieval utilization and reports oracle-passage EM split by whether the model already knew the
answer: Qwen2.5-3B (4-bit) reaches 12.8 EM on the Unknown split and 54.4 on the Known split, and
loses 45.6 points of previously correct answers to distraction. Our "EM given the answer was
retrieved" (n = 239) is the same conditional, computed on real retrieval rather than an oracle
passage, so call it "reader accuracy given retrieval success" and keep "reading fidelity" as the
page label. Report the complement (EM given absent) as the parametric residual and, if cheap, the
distraction rate: the share of closed-book-correct questions that the retrieve condition gets
wrong (Maekawa et al. 2024, arXiv 2402.13492, frame the same thing as "retrieval hurts").

### 2.7 The 2x2 and call precision, call recall

The decision to search versus closed-book correctness is a confusion matrix of the "retrieval
needed" label. Two literatures name its cells. Selective prediction (Geifman and El-Yaniv 2017,
arXiv 1705.08500; Geifman, Uziel, El-Yaniv 2019, arXiv 1805.08206) defines coverage as the share
of inputs the model answers without rejecting (here: silent) and selective risk as the error rate
on that share (here: silent when wrong divided by silent). Self-knowledge papers name the cells
directly: Ren et al. 2023 report the give-up rate and Right/G (gave up but would have been right,
our "called when right"); Yin et al. 2023 compute an F1 between the model's "I do not know" and
the true unknowns; Kadavath et al. 2022 evaluate P(IK) by its AUROC against actual correctness.
Our call precision (called when wrong over all calls) and call recall (called when wrong over all
closed-book-wrong) are precision and recall of the positive class "retrieval needed". Pitfall:
with closed-book EM at 3 to 6%, the always-call policy already has precision 0.94 to 0.97 and
recall 1.0, so both numbers are near their ceiling for any model that calls often; print the
always-call baseline in the same row and use the four raw counts as the headline. Whitehead et al.
2022 (arXiv 2204.13631) fold the asymmetry into one number, effective reliability: +accuracy for a
correct answer, minus a cost c for a wrong one, 0 for an abstention; the same formula applies if
"abstain" is read as "search".

### 2.8 Confidence gating from token log-probabilities

Three conventions apply. Selective QA (Kamath et al. 2020, arXiv 2006.09462) uses MaxProb, the
model's probability of its own answer, as the confidence, plots the risk-coverage curve, and
reports its area (AUC) and coverage at a target accuracy (their headline: 56.1% coverage at 80%
accuracy with a calibrator versus 48.2% with MaxProb). Correctness prediction (Kuhn, Gal, Farquhar
2023, arXiv 2302.09664; Farquhar et al. 2024, Nature 630:625) reports AUROC of the score against
correctness and AURAC, the area under the rejection-accuracy curve (accuracy on the kept fraction
as the least confident questions are dropped). Calibration (Guo et al. 2017, arXiv 1706.04599;
Jiang et al. 2021, arXiv 2012.00955 for QA) reports ECE, the binned mean absolute gap between
confidence and accuracy, and the Brier score. For gating retrieval, FLARE triggers when any token
of the next sentence falls below a probability threshold, and Moskvoretskii et al. 2025 show that
plain uncertainty scores (max or mean token entropy, lexical similarity of samples) match
Always-RAG accuracy with fewer retriever calls. Pitfall: AUROC needs both classes; at 30 correct
answers out of 592 its confidence interval is wide. AURC (Geifman 2019) depends on the base error
rate, so compare E-AURC or the curve, not the raw area.

### 2.9 Query quality

KILT (arXiv 2009.02252) scores retrieval at page level: R-precision is r/R over the provenance
pages, and with one provenance page it is precision@1 on the subject page, which is our metric.
KILT also gates the answer score on retrieval success (KILT-EM counts EM only when R-precision is
1), a joint version of our reading-fidelity split. Rewrite-Retrieve-Read (Ma et al. 2023) is the
paper to cite for "can the model write the query": a trainable rewriter lifts ChatGPT on PopQA
from EM 43.20 (retrieve-then-read) to 45.72. DRAGIN calls the step query formulation; Search-R1 and
ReAct call it the search action. Our finding that Gemma and Qwen's own queries (EM 0.40) beat the
heuristic shaped query (EM 0.31 and 0.28) is a rewrite-retrieve-read result.

### 2.10 Cost

Papers report cost in four currencies: tokens per query (Self-Route, as a share of the
long-context baseline: Gemini-1.5-Pro at 38.39% of the tokens for 46.41 versus 49.70), relative
time (Adaptive-RAG "Time", single-step = 1.00), retriever and LM calls per question (Moskvoretskii
RC and LMC; DRAGIN #Num; Adaptive-RAG Step), and seconds per query on stated hardware (TARG: +0.012
s over a 10.3 s baseline). The accuracy-versus-cost scatter with the non-dominated points joined is
called the Pareto frontier or accuracy-efficiency frontier (TARG, Snell et al. 2024). "Tokens per
correct answer" is not an established metric; if used, derive it as tokens per question divided by
EM and label it as such. "Retrieval budget" appears in ToolBench (a step budget) and in Adaptive-RAG
(steps), not as a fixed term.


## 3. Standard names for our conditions and roles

- Closed-book QA: the model answers from parameters (Roberts et al. 2020, arXiv 2002.08910, who
  chose the exam metaphor). Also "No Retrieval" (Jeong 2024), "Never RAG" (Moskvoretskii 2025),
  "Direct inference" (Search-R1), "vanilla LM" (Mallen 2023).
- Open-book or open-domain QA: the model may consult a corpus (DrQA, Chen et al. 2017, arXiv
  1704.00051, "machine reading at scale"; ORQA, Lee et al. 2019, arXiv 1906.00300, "open-retrieval
  QA"). Open-domain means the corpus is all of Wikipedia; our corpus is Danish Wikipedia intros.
- Retrieval-augmented generation: a generator conditioned on retrieved passages (Lewis et al.
  2020, arXiv 2005.11401; REALM, arXiv 2002.08909, for the pre-training version; RETRO, arXiv
  2112.04426, for chunked cross-attention; Atlas, arXiv 2208.03299, for few-shot).
- No-retrieval, always-retrieve, adaptive retrieval: the three policies of Mallen et al. 2023.
  Adaptive-RAG adds "Single-step" and "Multi-step" and reserves "Adaptive Retrieval" for Mallen's
  popularity rule and "Adaptive-RAG" for its classifier. Moskvoretskii 2025 and TARG use "Never RAG"
  and "Always RAG". Self-RAG says "on-demand" retrieval. Our "retrieve" is always-retrieve,
  single-step, k = 3. Our "agentic" is adaptive retrieval decided by the model itself.
- Oracle retrieval and gold passage: in the literature "oracle" or "gold passage" means the reader
  is given the document that contains the answer (DPR's gold contexts; Liu et al. 2023; arXiv
  2603.11513's "oracle condition"). Our retrieve-oracle gives the retriever the gold query (the
  Subject field) and the reader still sees three real search results, so call it oracle-query
  retrieval and say in one sentence that it upper-bounds query formulation, not reading.
- Interleaved or active or dynamic retrieval: retrieval inside generation, triggered by the text
  so far (IRCoT, Trivedi et al. 2022, arXiv 2212.10509; FLARE; DRAGIN; SeaKR, arXiv 2406.19215).
  We do not do this; our design is one round before the answer.
- Single-hop versus multi-hop: one passage suffices (NQ, TriviaQA, PopQA, DAISY) versus a chain of
  passages (HotpotQA, Yang et al. 2018, arXiv 1809.09600; 2WikiMultihopQA; MuSiQue). DAISY is
  single-hop; say so, because the adaptive-retrieval papers that report large gains are multi-hop.
- Self-ask: the model writes follow-up questions and answers them, optionally with a search engine
  (Press et al. 2022, arXiv 2210.03350). Related: ReAct's Thought, Action, Observation loop.
- Query rewriting or query generation: "rewrite-retrieve-read" (Ma et al. 2023, arXiv 2305.14283)
  names the roles rewriter, retriever, reader. DRAGIN says query formulation. Search-R1 and
  Toolformer say the model generates a search query. Our "shaped query" is a rule-based rewriter;
  our agentic query is a model rewriter.
- Retriever and reader: DrQA's split; every open-domain QA paper since keeps it. FiD (Izacard and
  Grave 2021, arXiv 2007.01282) is the reader that made retrieval scale to k = 100.
- "Asker": not an established term. Use "query generator" or "rewriter" for the component, and
  "the search action" for the act. If a role name is wanted for the whole decide-and-query step,
  the tool-use literature says "function calling" (Gorilla, arXiv 2305.15334; BFCL, ICML 2025;
  tau-bench, arXiv 2406.12045) and the agent literature says "action selection" (ReAct).
- "Agentic": in tau-bench and BFCL v3 it means multi-turn tool interaction with state; ours is a
  single-round decision. Write "single-round tool decision (the model chooses whether to search)"
  the first time and "agentic" afterwards.
- Tool use: Toolformer (Schick et al. 2023, arXiv 2302.04761) for self-supervised API calls;
  ToolLLM (Qin et al. 2023, arXiv 2307.16789) for pass rate and win rate over 16k APIs; Gorilla
  for AST-matched API calls and hallucinated APIs; BFCL for AST accuracy, executable accuracy and
  relevance detection (withholding the call when no function fits); tau-bench for pass^k, the
  chance that all k independent trials succeed, estimated per task as C(c, k) / C(n, k); MCP (Model
  Context Protocol, Anthropic, 25 Nov 2024, modelcontextprotocol.io) is the transport standard for
  tool schemas, not a metric.
- Decide-then-search: "priori judgement" (Ren et al. 2023) or "direct prompting for self-knowledge"
  (SKR); the verbalised cousin of P(IK) (Kadavath et al. 2022).
- Self-consistency: Wang et al. 2022, arXiv 2203.11171; majority vote over sampled answers; in 2024
  language a test-time scaling method (Snell et al. 2024, arXiv 2408.03314).
- Faithfulness versus factuality: faithfulness is consistency with the provided source, factuality
  is truth in the world (Maynez et al. 2020, arXiv 2005.00661). Attributable answers: "attributable
  to identified sources", AIS (Rashkin et al. 2021, arXiv 2112.12870; Bohnet et al. 2022, arXiv
  2212.08037). RAGAS (Es et al. 2023, arXiv 2309.15217) defines faithfulness as the share of answer
  statements supported by the context, answer relevance as similarity between the question and
  questions regenerated from the answer, and context relevance as the share of context sentences
  needed; context precision and context recall are library additions, not in the paper. With a
  single-string gold, our reading fidelity is a stricter, reference-based stand-in for faithfulness
  and our EM-given-absent is a factuality-without-support measure.
- Retrieval evaluation: recall@k and hit rate@k (share of questions with a relevant item in the top
  k), MRR (mean of 1/rank of the first relevant item), nDCG (graded, position-discounted). Our two
  retrieval numbers are answer recall@3 (string level) and precision@1 on the subject page (page
  level).


## 4. Recommended metric set and names for the results page and the letter

Headline set, in this order, with the name to print.

1. Exact match (EM), the benchmark's own scorer and normalisation. It is the number the group
   already publishes, so every comparison on the page is on their terms.
2. Contains-match accuracy ("lenient EM: gold string inside the answer", Mallen et al. 2023
   convention). It is the metric the adaptive-retrieval papers call accuracy, so it is the column
   to use when a reader compares our small models to Self-RAG or Adaptive-RAG.
3. Token F1, beside EM. It is the second official number and it shows the partial-match mass.
4. BLEU, in the replication table only, with one footnote on sentence-level smoothing. It is the
   paper's reported metric, so the replication must show it, and it says nothing beyond F1 on
   short answers.
5. Answer recall@3 ("retrieval ceiling: gold answer inside the top-3 intros"), under three query
   formulations. It is DPR's top-k retrieval accuracy and it separates what the corpus could give
   from what the model took.
6. Reader accuracy given retrieval success ("reading fidelity"), with n, plus EM given absent.
   It isolates the reader from the retriever, which is the question the committee cares about
   for a 1B model.
7. Distraction rate: share of closed-book-correct questions lost under retrieval. It is the
   number arXiv 2603.11513 makes central for sub-7B models and it costs nothing to compute.
8. Retrieval rate ("share of questions where the model searched"), which in our one-round design
   equals retriever calls per question. It is the cost axis every adaptive-retrieval paper
   reports.
9. The retrieval-necessity 2x2 with raw counts, printed with the always-call baseline in the
   same row; call precision and call recall as derived columns. The counts are honest at 3 to 6%
   closed-book accuracy, where the derived ratios are near their ceiling for any frequent caller.
10. Self-assessment accuracy for the scaffold: the share of wrong closed-book answers the model
    claimed to know ("silent-when-wrong rate" or, in Ren's terms, 1 minus the give-up rate on
    wrong answers). It is the calibration sentence for the letter and it maps to P(IK).
11. For the log-probability gate: AUROC of the confidence against closed-book correctness and the
    risk-coverage curve with coverage at a target accuracy. These are the selective-QA and
    hallucination-detection conventions and they do not require a calibrated probability.
12. Precision@1 on the subject page ("query quality"), for the agentic runs. It is KILT's
    page-level R-precision with one provenance page and it answers "can the model ask".
13. Tokens per question (prompt and generated, separately), seconds per question on the GTX 1060,
    retriever calls per question, and one accuracy-versus-tokens scatter with the Pareto frontier
    drawn. A group that publishes training-efficiency papers reads cost tables first.
14. Self-consistency (5 samples, majority vote) as one row per model, labelled test-time scaling.
    It is the honest touch for the ad's first topic and the result is a null.
15. Answer-type breakdown (year, number, text) with n. It is where the format failures live.

Names to avoid on the page: "oracle context" or "gold passage" for retrieve-oracle (it is an oracle
query); "hallucination rate" for silent-when-wrong (hallucination is a property of the answer, not
of the decision); "tokens per correct answer" as a headline (derived, non-standard); "agentic" without
the one-line definition; "accuracy" without saying which match rule.


## 5. Comparables: the closest published results

All numbers read from the cited source on 4 Sep 2026. "acc" means contains-match unless EM is
stated.

### 5.1 Retrieval-augmented small models against larger closed-book models

| System, size | Comparison | Benchmark, metric | Numbers | Citation |
|---|---|---|---|---|
| REALM, 330M, Wikipedia index | T5-11B closed-book | NQ, EM | REALM 40.4 (CC-News) and 39.2 (Wikipedia); T5-11B 34.5; ORQA 33.3 | Guu et al. 2020, arXiv 2002.08909, Table 1 |
| RAG-Sequence, BART-large 406M + DPR, k in {5, 10} | T5-11B+SSM closed-book | NQ, TQA, WQ, CT, EM | RAG-Seq NQ 44.5, TQA 56.8 (wiki test 68.0), WQ 45.2, CT 52.2; T5-11B+SSM NQ 36.6, TQA 60.5, WQ 44.7 | Lewis et al. 2020, arXiv 2005.11401, Table 1 |
| Closed-book scaling | T5-Base to T5-11B | NQ dev, EM | 25.9, 28.5, 30.4, 32.6, then 34.8 with salient-span masking; 62% of "wrong" NQ answers were true positives on manual check | Roberts et al. 2020, arXiv 2002.08910 |
| RETRO 7.5B, 2T-token database | GPT-3 175B, Jurassic-1 178B, Gopher 280B | The Pile, bits per byte | "comparable performance to GPT-3 and Jurassic-1 on the Pile, despite using 25x fewer parameters"; beats Jurassic-1 and Gopher on a majority of Pile test sets | Borgeaud et al. 2021, arXiv 2112.04426 |
| RETRO 7.5B fine-tuned | REALM, RAG, DPR, FiD | NQ, EM | RETRO 45.5; REALM 40.4; DPR 41.5; RAG 44.5; FiD 51.4; FiD+Distill 54.7 | same, Table 5 |
| Atlas 11B, 64-shot, Contriever, Wikipedia Dec 2021 + CommonCrawl | PaLM 540B, Chinchilla 70B, Gopher 280B, GPT-3 175B | NQ and TQA, 64-shot, EM | NQ: Atlas 42.4, PaLM 39.6, Chinchilla 35.5, GPT-3 29.9, Gopher 28.2. TQA: Atlas 74.5, Chinchilla 64.6, Gopher 57.2. Full fine-tune: NQ 64.0, TQA filtered 79.8 | Izacard et al. 2022, arXiv 2208.03299 |
| Toolformer, GPT-J 6.7B with Wikipedia search (used in 99.3% of QA examples) | GPT-3 175B, OPT 66B | WebQS, NQ, TQA; correct answer within the first 20 words | Toolformer 26.3 / 17.7 / 48.8; GPT-J 18.5 / 12.8 / 43.9; GPT-3 29.0 / 22.6 / 65.9; OPT-66B 18.6 / 11.4 / 45.7 | Schick et al. 2023, arXiv 2302.04761, Table 5 |
| ReAct, PaLM-540B, Wikipedia search/lookup/finish | Standard, CoT, CoT-SC | HotpotQA EM, FEVER acc | Standard 28.7 / 57.1; CoT 29.4 / 56.3; CoT-SC 33.4 / 60.4; Act 25.7 / 58.9; ReAct 27.4 / 60.9; ReAct then CoT-SC 35.1 / 62.0 | Yao et al. 2022, arXiv 2210.03629 |
| Self-RAG 7B and 13B, Contriever-MS MARCO, k = 5 | ChatGPT, Llama2-7B/13B with and without retrieval | PopQA acc, TQA-unfiltered acc | PopQA: Self-RAG 7B 54.9, 13B 55.8; ChatGPT 29.3 (50.8 with retrieval); Llama2-7B 14.7 (38.2); Llama2-13B 14.7 (45.7); Alpaca-7B 23.6 (46.7). TQA: Self-RAG 66.4 / 69.3; ChatGPT 74.3 (65.7 with retrieval); Llama2-7B 30.5 (42.5) | Asai et al. 2023, arXiv 2310.11511, Table 2 |

### 5.2 Adaptive retrieval: accuracy and cost

| System, model | Policy | Benchmark, metric | Accuracy | Cost | Citation |
|---|---|---|---|---|---|
| Mallen 2023, GPT-3 davinci-003 | popularity threshold per relation | PopQA (14k), acc | adaptive with GenRead + Contriever 46.5, "5.3% higher than any non-adaptive method" | retrieves for 40% of questions (with BM25); "reducing GPT-3 API costs by half"; inference time down "up to 9%" (figures 9 to 11) | arXiv 2212.10511 |
| Adapt-LLM, Llama-2 7B trained to emit a RET token | learned request | PopQA, EM | Never-retrieve about 21; Always-retrieve about 36; Adapt-LLM 36.77 (NQ-trained), 38.15 (SQuAD-trained); popularity rule 36.81 | retrieval on 82.26% and 83.93% of questions; popularity rule retrieves on 99.86% | Labruna et al. 2024, arXiv 2404.19705 |
| Adaptive-RAG, FLAN-T5-XL 3B, six datasets, 500 questions each | classifier chooses none / single / multi | mean of SQuAD, NQ, TQA, MuSiQue, HotpotQA, 2Wiki; EM / F1 / acc | No retrieval 14.87 / 21.12 / 15.97; Single-step 34.83 / 44.31 / 38.87; Multi-step 39.00 / 48.85 / 43.70; Adaptive Retrieval (Mallen rule) 23.87 / 32.24 / 26.73; Self-RAG 9.90 / 20.79 / 31.57; Adaptive-RAG 37.17 / 46.94 / 42.10 | Step / Time (relative to single-step): 0 / 0.11; 1.00 / 1.00; 4.69 / 8.81; 0.50 / 0.56; 0.72 / 0.43; 2.17 / 3.60 | Jeong et al. 2024, arXiv 2403.14403, Table 1 |
| Adaptive-RAG, FLAN-T5-XXL 11B | same | same | No retrieval 17.83; Single 37.87; Multi 40.13; Adaptive-RAG 38.90 EM | Adaptive-RAG 1.35 steps, 2.00 time | same |
| FLARE, text-davinci-003 | token probability below theta triggers retrieval | 2WikiMultihopQA, EM / F1 | No retrieval 28.2 / 36.8; single-time 39.4 / 48.8; FLARE 51.0 / 59.7; StrategyQA 77.3 | retrieval triggered for 30 to 60% of sentences | Jiang et al. 2023, arXiv 2305.06983 |
| DRAGIN, LLaMA2-13B-Chat | entropy times attention triggers retrieval; self-attention forms the query | 2Wiki, EM / F1 | without RAG 0.187 / 0.272; single retrieval 0.245 / 0.336; FLARE 0.224 / 0.308; DRAGIN 0.304 / 0.393 | retrieval calls per question: DRAGIN 2.5 to 4.8; FLARE 0.6 to 5.5; FL-RAG 3.2 to 4.2 | Su et al. 2024, arXiv 2403.10081, Tables 2 and 3 |
| SeaKR, LLaMA-2-7B-chat | Gram-determinant uncertainty of hidden states | NQ, TQA, SQuAD, 2Wiki; EM / F1 | NQ 25.6 / 35.5; TQA 54.4 / 63.1; SQuAD 27.1 / 36.5; 2Wiki 30.2 / 36.0 | k = 3, at most one retrieval step on single-hop | Yao et al. 2024, arXiv 2406.19215 |
| Moskvoretskii 2025, Llama-3.1-8B-Instruct, 35 methods | uncertainty scores as gates | NQ, In-Accuracy | Never RAG 0.446; Always RAG 0.496; Adaptive-RAG 0.496; FLARE 0.450; DRAGIN 0.480; SeaKR 0.406; Max Entropy 0.506; Lexical Similarity 0.512; EigValLaplacian 0.512 | RC / LMC per question: Never 0 / 1.0; Always 1.00 / 1.0; Adaptive-RAG 0.98 / 2.0; FLARE 2.07 / 3.1; DRAGIN 2.24 / 4.5; Rowen Hybrid 7.27 / 55.0; SeaKR 1.00 / 14.6; Lexical Similarity 0.58 / 1.6 | arXiv 2501.12835 |
| TARG (2025), Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct | prefix entropy or top-1/top-2 margin on a no-context draft | TQA and NQ-Open, EM / F1 | Qwen TQA: Never 60.8, Always 57.6, TARG-Margin 62.2. Llama NQ-Open: Never 53.8, Always 48.6, TARG-Margin 57.6 | retrieval rate 0.338 (Qwen TQA) and 0.008 (Llama NQ); latency +0.012 s per query over a 10.299 s baseline; "reducing retrieval by 70 to 90%" | arXiv 2511.09803 |
| DeepRAG (2025), Llama-3-8B-Instruct | learned step-wise retrieval | mean over HotpotQA, 2Wiki, CAG, PopQA, WebQuestions; EM / F1 | CoT 27.20 / 37.75; CoT-Retrieve 34.90 / 46.85; FLARE 23.80 / 32.88; DRAGIN 27.60 / 38.05; DeepRAG 40.70 / 51.54 | WebQuestions retrievals per question: DeepRAG 0.28, TAARE 0.66, IterDRAG 2.25, Auto-RAG 4.52 | Guan et al. 2025, arXiv 2502.01142 |
| ReaLM-Retrieve (2026), reasoning models | step-level uncertainty detector | MuSiQue, HotpotQA, 2Wiki; F1 | +10.1 F1 absolute over standard RAG (9.0 to 11.8 across sets); MuSiQue 71.2 F1 | 1.8 retrieval calls per question; 47% fewer calls than IRCoT; Recall@5 81.3 | Guo, Wu, Yiu 2026, arXiv 2604.26649 |
| Self-Route (2024), Gemini-1.5-Pro, GPT-4O | route to RAG or long context by self-reflection | LongBench and InfiniteBench, mean score | Gemini: LC 49.70, RAG 37.33, Self-Route 46.41; GPT-4O: LC 48.67, RAG 32.60, Self-Route 48.89 | tokens as share of LC: 38.39% (Gemini), 61.40% (GPT-4O); "cost is reduced by 65% for Gemini-1.5-Pro and 39% for GPT-4O" | Li et al. 2024, arXiv 2407.16833 |
| SKR, ChatGPT | self-knowledge by kNN over training questions | mean of five QA sets | no retrieval 67.89; always retrieve 67.77; SKR-kNN 70.62 | not reported as calls | Wang et al. 2023, arXiv 2310.05002 |
| Probing-RAG | prober on intermediate hidden states | five open-domain QA sets | "outperforms previous methods while reducing the number of redundant retrieval steps" | steps reduced (paper) | Baek et al. 2024, arXiv 2410.13339 |

### 5.3 Open 1B to 4B models with Wikipedia retrieval on NQ, TriviaQA, PopQA

| Model | Setting | NQ | TQA | PopQA | Citation |
|---|---|---|---|---|---|
| Qwen2.5-3B (base), Wikipedia 2018, E5, k = 3 | Direct inference, EM | 0.106 | 0.288 | 0.108 | Search-R1, arXiv 2503.09516 v5, Table 2 |
| same | RAG (always retrieve), EM | 0.348 | 0.544 | 0.387 | same |
| same | IRCoT, EM | 0.111 | 0.312 | 0.200 | same |
| same | Search-R1 (RL-trained search), EM | 0.406 | 0.587 | 0.435 | same |
| Qwen2.5-3B-Instruct | Search-R1, EM | 0.341 | 0.545 | 0.378 | same |
| Qwen2.5-7B-Instruct | Direct / RAG / Search-R1, EM | 0.134 / 0.349 / 0.393 | 0.408 / 0.585 / 0.610 | 0.140 / 0.392 / 0.397 | same |
| Qwen-2.5-3B (base), Google via SerpAPI at test time | ZeroSearch, EM | 43.0 | 61.6 | 41.4 | Sun et al. 2025, arXiv 2505.04588 |
| Llama-3.2-3B (base), same | ZeroSearch, EM | 43.4 | 63.8 | 48.4 | same |
| Qwen2.5-3B-Instruct, 4-bit, 500k-passage Wikipedia subset | oracle-passage EM 12.8 on the Unknown split (closed-book wrong) and 54.4 on the Known split; 45.6 points of Known answers lost to distraction | mixed NQ and HotpotQA, 1,000 questions | n/a | n/a | arXiv 2603.11513 (2026) |
| Qwen2.5-1.5B-Instruct, 4-bit | oracle-passage EM 10.0 (Unknown), 43.0 (Known); 57.0 points lost | same set | n/a | n/a | same |
| SmolLM2-360M | oracle-passage EM 0.0 | same set | n/a | n/a | same |

The 2026 study's summary sentence is the one to quote against our reading-fidelity numbers: "even
with oracle retrieval, models <= 7B fail to extract the correct answer 85 to 100% of the time on
questions they cannot answer alone." Our conditional EM given retrieval success (Mimir 0.59, Llama
1B 0.37, Gemma 4B 0.73) is higher because DAISY answers are short entity strings that sit in the
first paragraph, and because our conditional is on questions with the answer literally present,
not on the Unknown split; say both when comparing.

### 5.4 Closed-book knowledge numbers for the model families we ran

| Model | TriviaQA | NQ | Protocol | Citation |
|---|---|---|---|---|
| Gemma 3 1B (pretrained) | 39.8 | 9.48 | 5-shot, accuracy | Gemma 3 technical report, arXiv 2503.19786, Table 9 |
| Gemma 3 4B (pretrained) | 65.8 | 20.0 | 5-shot | same |
| Gemma 3 12B / 27B | 78.2 / 85.5 | 31.4 / 36.1 | 5-shot | same |
| Gemma 2 2B / 9B / 27B | 60.2 / 76.5 / 83.8 | 17.2 / 29.2 / 34.7 | 5-shot | same |
| Llama 3.1 8B (base) | 77.6 (TriviaQA-Wiki, EM) | not reported | 5-shot | meta-llama/Llama-3.1-8B model card |
| Llama 3.2 1B / 3B | not reported | not reported | the 3.2 model card lists MMLU, ARC, SQuAD, QuAC, DROP only | meta-llama/Llama-3.2-3B-Instruct model card |
| Qwen2.5 0.5B / 1.5B / 3B | not reported | not reported | the Qwen2.5 report (arXiv 2412.15115) Table 5 has MMLU, BBH, ARC-C, TruthfulQA, GSM8K, HumanEval, MBPP | Qwen2.5 technical report |

### 5.5 Danish and Scandinavian QA

| Source | What it is | Numbers | Citation |
|---|---|---|---|
| DAISY | 741 close-ended QA pairs from the Danish Culture Canon 2006, generated from Wikipedia pages, human-approved; zero-shot, BLEU and F1 | Llama-3.3-70B-Instruct 0.166 / 0.268 (best); gpt-oss-120b 0.126 / 0.211; Mistral-Small-3.1-24B 0.124 / 0.202; gemma-3-27b-it 0.123 / 0.193; gpt-oss-20b 0.062 / 0.112 (BLEU / F1) | Nielsen, Beltoft, Schneider-Kamp, Galke 2026, arXiv 2601.19930 |
| Mimir v1 | 1B HRM, permissible post-training data; Daisy as EM, zero-shot greedy | Mimir 1B 9.6; Gemma 4 E2B 5.6; Munin-Qwen 9B 5.4; Qwen 3.5 4B 4.7; Gemma 3 1B 1.4; Qwen 3.5 0.8B 0.7; HRM-Text 1B 0.0; OLMo 2 1B 0.0 | Schneider-Kamp et al. 2026, arXiv 2608.13517, Table 9 |
| Our replication on the 592 public golds | the group's own prediction files, their scorer | Llama-3.3-70B EM 0.225, F1 0.277, BLEU 0.172; gpt-oss-120b EM 0.171; gemma-3-27b EM 0.171; gpt-oss-20b EM 0.074 | results/RESULTS.md |
| MKQA | 10k NQ-derived questions aligned across 26 languages including Danish (da); EM and F1; answers may be extracted, generated or from a knowledge graph | English baseline 45.39 EM / 51.97 F1 (XLM-R Large translate-train); best overall F1 46.0 | Longpre, Lu, Daiber 2020, arXiv 2007.15207 |
| ScandEval / ScandiQA-da | Danish reading comprehension built from MKQA and NQ; gold passage given; EM and F1 | task-level numbers per model on the leaderboard, not in the paper | Nielsen 2023, arXiv 2304.00906 |
| Danoliterate | eight Danish scenarios (citizenship test, HyggeSwag, Gym 2000, #twitterhjerne, Nordjylland News, cloze, DaNE, Angry Tweets); correlation with human ranking about 0.8 | no retrieval scenario; calibration and toxicity announced but unreleased | Holm, Hansen, Nielsen 2024, arXiv 2410.22839 |

No published Danish open-domain or retrieval-augmented QA number was found (searched 4 Sep 2026:
MKQA is used as reading comprehension in ScandEval, Danoliterate has no retrieval scenario, XOR-QA
and CORA and MIRACL and NoMIRACL do not include Danish). The nearest comparables for our retrieval
rows are therefore the English PopQA numbers in 5.3 and the group's own closed-book Daisy table.
State that gap on the page in one sentence; it is a contribution, not a weakness.

### 5.6 Published cost figures for adaptive retrieval, collected

- Retriever calls per question: Moskvoretskii 2025 (NQ, Llama-3.1-8B): Always RAG 1.00, Adaptive-RAG
  0.98, Lexical Similarity gate 0.58, Max Entropy gate 0.73, FLARE 2.07, DRAGIN 2.24, Rowen 7.27.
  DRAGIN: 2.5 to 4.8 across datasets. DeepRAG on WebQuestions: 0.28. ReaLM-Retrieve on MuSiQue: 1.8.
- LM calls per question: Moskvoretskii 2025: Always RAG 1.0, Adaptive-RAG 2.0, FLARE 3.1, DRAGIN 4.5,
  SeaKR 14.6, Rowen Hybrid 55.0.
- Retrieval rate (share of questions that retrieve): Mallen 2023 GPT-3 40%; Adapt-LLM 82 to 84%
  (7B on PopQA); TARG 0.8% to 34% (7B to 8B on NQ and TQA); Adaptive-RAG "Step" 2.17 for a 3B model
  (multi-step counted).
- Relative time: Adaptive-RAG (3B): no retrieval 0.11, single-step 1.00, multi-step 8.81,
  Adaptive-RAG 3.60.
- Tokens: Self-Route 38.39% and 61.40% of long-context tokens (Gemini-1.5-Pro, GPT-4O). Search-R1
  and ZeroSearch do not report tokens per question in the main table.
- Wall-clock: TARG +0.012 s per query over 10.299 s (Llama-3.1-8B, NQ-Open). Mallen: always-retrieve
  "almost doubles" inference latency on GPT-J 6B; adaptive cuts it by up to 9%.


## 6. Pitfalls

1. EM against contains-match. The adaptive-retrieval papers (Mallen, Self-RAG, Adaptive-RAG,
   Moskvoretskii, Toolformer) report contains-match and call it accuracy; DPR, RAG, Atlas, RETRO,
   Search-R1 and the Mimir paper report strict EM. Comparing our strict EM to their "acc"
   understates us; comparing our lenient column to their EM overstates us. Label every
   cross-paper comparison with the match rule. Both rules have both error directions (Roberts:
   62% of EM-wrong NQ answers were right; contains-match scores a year inside an unrelated sentence).
2. BLEU on one-word answers. Sentence BLEU with smoothing method 4 is a length-penalised unigram
   precision at these lengths. It ranks systems by answer length as much as by correctness. Keep it
   in the replication table only.
3. AUROC against AURC. AUROC is threshold-free and base-rate-free but unstable with 30 positives
   in 592. AURC is base-rate dependent (a model with 5% accuracy has AURC near 0.95 whatever its
   confidence does); use E-AURC (Geifman 2019) or plot the curve and read coverage at a target
   accuracy (Kamath 2020). Farquhar 2024 uses AURAC, the accuracy-side mirror of AURC.
4. Selective risk against abstention rate. Risk is undefined at zero coverage and trivially low
   near it; abstention rate is 1 minus coverage. A model that searches on everything has zero
   silent-when-wrong and is not thereby calibrated. Report the pair, or the effective reliability
   with a stated cost c (Whitehead 2022).
5. Call precision at near-zero closed-book accuracy. With EM at 3 to 6%, "always search" has
   precision 0.94 to 0.97 and recall 1.0. Our Qwen (574 / 0 / 18 / 0) is the always-call policy;
   its precision says nothing about self-knowledge. Print the counts and the always-call baseline,
   and name the interesting cell: silent when wrong. Mallen's own finding is that small models
   should retrieve on almost everything, so a near-always caller is the correct policy here and the
   self-knowledge question needs a model that knows a lot (their 70B result is the place to say it).
6. Oracle query is not gold passage. The literature's "oracle" or "gold passage" means the answer
   document is handed to the reader with no distractors (Liu 2023: 88.3 against 56.1 closed-book).
   Ours hands the retriever the subject title and the reader still sees three search results,
   0.787 of which contain the answer. Say "oracle query" and give the ceiling next to it.
7. Retrieval ceiling with string match on intros. The ceiling counts literal presence in the lead
   sections of three pages; it is a property of the snippet policy. Numbers and years produce false
   presence; paraphrased facts produce false absence. State k, the snippet length and the corpus
   date in the model card.
8. Conditional reading fidelity mixes reader skill with question mix. The n = 239 "answer present"
   subset is the same for every model in the retrieve condition (same shaped query, same cache), so
   cross-model comparison is fair there; it is not fair across conditions with different queries.
   Compare reading fidelity across models within one condition only.
9. Provenance leak by construction. DAISY questions were generated from Wikipedia pages; retrieving
   from Danish Wikipedia by the subject title is retrieval from the benchmark's own provenance, as in
   KILT. It makes the oracle ceiling an honest upper bound and the shaped-query ceiling the realistic
   one. Say it plainly and the reviewer cannot say it for you.
10. Latency across architectures is not size. Mimir's HRM loop decodes at 4.2 tokens per second
    against 86 for Llama 1B on the same GTX 1060 with the same llama.cpp build. Seconds per
    question compares implementations; tokens per question compares policies. Report both, with
    hardware, quantisation (Q8_0), context (12288), batch (-np 3) and the KV-cache type.
11. Self-consistency needs sampling. Temperature 0 with five votes is five identical answers.
    Report the temperature, the sample count and the normalisation used before voting; ties broken
    how. With closed-book EM this low, the null is expected (Snell 2024: test-time compute helps
    when the base model has non-trivial per-sample accuracy).
12. "Agentic" is overloaded. tau-bench and BFCL v3 mean multi-turn, stateful tool use; ours is a
    single-round decision. Define it on first use.
13. Few-shot changes the protocol. The DAISY and Mimir protocols are zero-shot; agentic-fewshot
    is a different protocol and must not be compared to their table without the label.
14. Answer-type formatting. Numbers with units and Danish thousand separators ("1.500") break EM
    both ways; years inside phrases ("i 1998") fail strict EM and pass lenient. The year / number /
    text split is where to show this; do not fold it into the headline.
15. Popularity is missing. PopQA's adaptive retrieval keys on Wikipedia page views; DAISY has no
    popularity field. Page views of the subject page are one API call away and would let the
    Mallen rule be run on DAISY as a baseline for the model-decided policy; name it as next work.
16. Retrieval hurts. arXiv 2603.11513 reports 42 to 100% of previously correct answers destroyed by
    adding context in sub-7B models; Maekawa 2024 and TARG report Always-RAG below Never-RAG on TQA
    and NQ for 7B to 8B models. Our closed-book base is so low that the harm cannot show; compute
    the distraction rate anyway and report it as small n.
17. Citations without arXiv ids: BFCL is ICML 2025, PMLR v267 pages 48371 to 48392 (OpenReview
    2GmDdhBdDk), no arXiv id; Farquhar et al. 2024 is Nature 630:625 to 630, doi
    10.1038/s41586-024-07421-0, with the method paper at arXiv 2302.09664; MCP has no paper; SSIM,
    Shannon and Wyner-Ziv are journal papers cited above.
