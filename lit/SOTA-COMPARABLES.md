# Best-in-field comparables for the DAISY tool study

Written 4 Sep 2026 for the daisy-tools results page and the 4203 letter. Every number below was read
from the cited paper, model card or leaderboard on 4 Sep 2026. Numbers copied from a table carry the
table number. Numbers read off a plot say "read from figure" and are accurate to about 0.01 to 0.02.
Anything that could not be confirmed from a primary source is marked UNVERIFIED and must not be
quoted. Sibling files: GROUP-PAPERS.md (the Odense group's own protocol and numbers) and
METRICS-AND-TERMS.md (metric definitions and naming). Our own numbers are in results/RESULTS.md.

Contents

1. Danish and Scandinavian QA and knowledge benchmarks
2. English entity-centric short-answer QA: PopQA, TriviaQA, NQ, and the adaptive retrieval papers
3. Small model plus retrieval beats a much larger model: the canonical results
4. Industry search-augmented and tool-use evaluations
5. Calibration, self-knowledge and selective QA
6. Cost accounting conventions in adaptive retrieval papers
7. What our numbers look like next to these
8. Records we could try to beat on identical terms
9. Not found, unverified, and the bibliography

Our conditions, for reference (592 public DAISY questions, greedy, 0-shot, the group's prompt and
scorer, strict EM after ASCII normalisation; details in RESULTS.md):

| Condition | LM calls | Retriever calls | Llama 3.2 1B | Mimir 1B | Qwen 2.5 3B | Llama 3.2 3B | Gemma 3 4B |
|---|---|---|---|---|---|---|---|
| closed-book | 1 | 0 | 0.008 | 0.056 | 0.030 | 0.041 | 0.056 |
| retrieve (shaped query, top-3 da.wikipedia intros) | 1 | 1 | 0.152 | 0.265 | 0.279 | 0.282 | 0.311 |
| retrieve-oracle (benchmark subject as query) | 1 | 1 | 0.392 | 0.606 | 0.628 | 0.644 | 0.679 |
| agentic (model writes one SEARCH line or answers) | 1 + call rate | call rate | 0.008 (0 calls) | 0.049 (0 calls) | 0.400 (592 calls) | 0.037 (0 calls) | 0.399 (553 calls) |
| agentic-scaffold (yes/no self-check, then search on no) | 2 + call rate | call rate | 0.150 | 0.120 | 0.275 | 0.066 | 0.289 |
| group's Llama 3.3 70B closed-book, rescored on the 592 | 1 | 0 | 0.225 | | | | |

Retrieval ceilings (gold string inside the top-3 intros): question as query 0.215, shaped query 0.404,
subject as query 0.787. Reading fidelity in the retrieve condition (EM when the gold string was in the
intros): Gemma 3 4B 0.728, Llama 3B 0.665, Qwen 3B 0.644, Mimir 0.590, Llama 1B 0.368.

Metric vocabulary used below: EM = strict exact match after normalisation (ours); acc(contains) = the
gold string appears anywhere in the prediction (PopQA, Self-RAG, CRAG, "InAcc"); LLM-judge = a model
grades semantic equivalence (SimpleQA, BrowseComp, FRAMES); F1 = token overlap; MCC = Matthews
correlation on multiple choice (EuroEval); RC = retriever calls per question; LMC = LM calls per
question.

---

## 1. Danish and Scandinavian QA and knowledge benchmarks

### 1.1 DAISY itself and the Mimir report (the only Danish short-answer factual QA numbers that exist)

| Benchmark, setting | Model | Size | Metric | Number | Citation | Comparable to DAISY-with-lookup? |
|---|---|---|---|---|---|---|
| DAISY, 741 q, 0-shot closed-book | Llama-3.3-70B-Instruct | 70B | BLEU / F1 | 0.166 / 0.268 | arXiv 2601.19930 (Nielsen, Beltoft, Schneider-Kamp, Galke), Table 2 | Same task, no retrieval; scored on 741 not 592; no EM reported. Our rescoring of their prediction file on the 592: EM 0.225, F1 0.277, BLEU 0.172 |
| same | gpt-oss-120b | 120B | BLEU / F1 | 0.126 / 0.211 | same, Table 2 | our rescoring: EM 0.171 |
| same | Mistral-Small-3.1-24B-Instruct-2503 | 24B | BLEU / F1 | 0.124 / 0.202 | same, Table 2 | our rescoring: EM 0.169 |
| same | gemma-3-27b-it | 27B | BLEU / F1 | 0.123 / 0.193 | same, Table 2 | our rescoring: EM 0.171 |
| same | gpt-oss-20b | 20B | BLEU / F1 | 0.062 / 0.112 | same, Table 2 | our rescoring: EM 0.074 |
| DAISY (HF split, 592 q), 0-shot, greedy, Inspect AI | DFM Mimir 1B | 1.3B non-embedding + 0.4B embedding | EM | 9.6 | arXiv 2608.13517 (DFM Mimir v1 report), Table 9 | Same 592 rows, same metric, closed-book. Our Mimir closed-book 5.6 (causal-only llama.cpp port; see GROUP-PAPERS.md 3.2) |
| same | Munin-Apertus 8B | 8B | EM | 12.5 | same, Table 9 | highest closed-book EM in the table |
| same | Munin-Mistral 8B | 8B | EM | 8.4 | same, Table 9 | |
| same | Munin-Qwen 9B | 9.7B | EM | 5.4 | same, Table 9 | |
| same | Gemma 4 E2B (think) / Gemma 4 E2B | 2.3B effective | EM | 5.1 / 5.6 | same, Table 9 | the published 1 to 4B ceiling for a general model |
| same | Qwen 3.5 4B / 2B / 0.8B | | EM | 4.7 / 2.5 / 0.7 | same, Table 9 | |
| same | SmolLM3 3B | 3B | EM | 2.2 | same, Table 9 | |
| same | Gemma 3 1B / OLMo 2 1B / HRM-Text 1B | 1B | EM | 1.4 / 0.0 / 0.0 | same, Table 9 | our Llama 3.2 1B 0.8 sits here |
| Multi Wiki QA (da), 0-shot, passage given, 32 tokens | DFM Mimir 1B | | EM | 66.8 | same, Table 9 | Danish Wikipedia passage in context, short verbatim answer: the reading half of our task with a guaranteed hit |
| same | Gemma 4 E2B (think) / Qwen 3.5 4B / Munin-Qwen 9B | | EM | 59.3 / 57.1 / 55.7 | same, Table 9 | |
| same | Gemma 3 1B / Qwen 3.5 0.8B / OLMo 2 1B / SmolLM3 3B | | EM | 42.6 / 41.6 / 8.4 / 0.3 | same, Table 9 | |

DAISY paper protocol (arXiv 2601.19930, Sec. 3 and App. B): 741 pairs generated by Gemma 3 27B (4-bit)
from the Danish Wikipedia pages of the culture canon works, five per work, human validated; zero-shot
"Prompt Template Version 1"; case, punctuation, article and whitespace normalisation; word-level F1;
NLTK sentence_bleu with SmoothingFunction().method4; gpt-oss-20b answers over 2000 reasoning tokens
dropped. Mimir report protocol (arXiv 2608.13517, Sec. 5 and Table 11): greedy, temperature 0, seed
4242, all Danish tasks 0-shot, EM, Inspect AI, dataset schneiderkamplab/SDU-Daisy. Neither paper has
a retrieval condition. Mimir's training mix contains Danish Wikipedia derived instruction data
(synquid wiki-instruct-da, 0.99B tokens, Table 1) and the report's memorisation audit (Tables 12 to
13) tests verbatim regurgitation, not benchmark overlap.

### 1.2 EuroEval Danish leaderboard (euroeval.com/leaderboards/Monolingual/danish, data stamp 30 Aug 2026, fetched 4 Sep 2026, dataset versions 18.0.0)

Primary / secondary metric per task. Knowledge tasks are multiple choice (Citizen Tests 2 to 3 options,
Talemaader 4 options) with answer keys that exist online, so accuracy is not comparable to DAISY EM;
the DAISY paper itself makes this criticism of the citizenship test (Sec. 5.1). MultiWikiQA-da
(F1 / EM, 4-shot, answer guaranteed in the passage) is the closest published Danish task to our
reading step.

| Task | Top 3 (primary / secondary) | Best model under 5B | Llama 3.2 1B Inst | Llama 3.2 3B Inst | Gemma 3 4B it | Qwen 2.5 3B Inst | Llama 3.3 70B | Mimir (val) |
|---|---|---|---|---|---|---|---|---|
| Danish Citizen Tests (MCC / acc) | 100 / 100 for gemini-3.7-flash, gemini-3-flash-preview#thinking, gpt-5.5, gemini-2.5-pro, claude-3-7-sonnet#thinking | Qwen3.5-4B 77.30 / 84.89 | 0.93 / 35.35 | 44.55 / 61.50 | 53.91 / 69.09 (q4_0 GGUF via ollama, partial row) | not on board | 93.65 / 95.75 | 54.38 / 69.22 |
| Danske Talemaader (MCC / acc) | gemini-3-flash-preview#thinking 98.50 / 98.91; gpt-5.5 96.36 / 97.34; gemini-2.5-pro 95.12 / 96.41 | Ministral-3-3B-Base 63.07; Qwen3.5-4B 55.39 / 66.56 | -0.49 / 23.54 | 18.45 / 37.66 | 44.03 / 56.73 (q4_0) | not on board | not run | 25.69 / 44.53 |
| MultiWikiQA-da (F1 / EM) | Olmo-3-1125-32B 83.76 / 69.88; Ministral-3-14B-Base 82.94 / 70.54; Mistral-Small-3.2-24B 82.73 / 66.46 | DFM-Mimir (zero-shot) 79.94 / 66.25 | 8.63 / 0.00 | 70.23 / 52.62 | not run | not on board | 70.18 / 41.74 | 78.84 / 65.16 |
| DaLA (MCC) | DFM-Mimir (zero-shot) 92.45; DFM-Mimir 86.12; gemini-3.7-flash 77.43 | Mimir | 0.41 | 8.05 | not run | not on board | not run | 86.12 |
| Nordjylland News (BERTScore) | gemma-4-31B-it 38.52; Qwen3.5-27B-FP8 38.51; Qwen3.5-35B-A3B 38.49 | deahmed/Qwen3.5-2B-da-task 37.17 | 29.30 | 36.01 | 36.77 (bf16) | not on board | 37.58 | 36.82 |
| Overall rank score (lower is better) | gemini-3-flash-preview#thinking 1.25; gemini-3.7-flash 1.26; gpt-5.5 1.26 | Qwen3.5-4B 2.26 | 3.85 | 2.95 | unranked | not on board | unranked | 1.85 |

Other Danish-relevant rows on the same board: munin-qwen3.5-9B Citizen 82.13 / 87.83, Talemaader
76.63 / 82.46, MultiWikiQA 79.53 / 61.46; munin-7b-alpha Citizen 71.18 / 80.55, Talemaader 31.46 /
46.32, MultiWikiQA 74.94 / 60.05; snakmodel-7b-instruct Citizen 41.75 / 59.24; Viking-33B Citizen
32.14 / 53.73, Talemaader 8.92 / 30.56; Viking-7B Citizen -1.88 / 35.12; Llama-Poro-2-70B-Instruct
Citizen 84.66 / 89.66, Talemaader 78.14 / 83.63; gpt-sw3-40b Citizen 18.39 / 44.74, Talemaader 8.75 /
28.35, MultiWikiQA 73.22 / 58.78; gpt-sw3-1.3b Citizen 4.48 / 37.07, MultiWikiQA 56.18 / 42.73;
gemma-4-E2B-it Citizen 54.78 / 69.56, Talemaader 44.82 / 58.59, MultiWikiQA 71.90 / 53.52;
Qwen3.5-2B Citizen 37.68 / 58.56, MultiWikiQA 72.55 / 54.66; gemma-3-1b-it Citizen 15.95 / 43.98,
MultiWikiQA 17.01 / 0.00. GPT-4o and Claude 3.x are absent from the 30 Aug 2026 board; the last
published GPT-4o Danish rank score is 1.46 (gpt-4o-2024-05-13) in arXiv 2406.13469, Table 4.

Current official Danish generative tasks and sizes (EuroEval docs, same bundle): Angry Tweets 2,048
(12-shot, MCC); DANSK NER 1,024 (8-shot, micro-F1); DaLA 2,048 (12-shot, MCC; arXiv 2512.04799);
MultiWikiQA-da 2,048 of 5,000 (4-shot, F1 / EM; arXiv 2509.04111); DanWiC 916 (MCC); Nordjylland
News 2,048 (BERTScore); Danske Talemaader 808 of 1,000 (MCC); Danish Citizen Tests 525 of 870 (MCC);
Winogrande-da 1,085 (5-shot, MCC; arXiv 2506.19468). ScandiQA-da, DanFEVER, ScaLA-da and HellaSwag-da
are no longer official Danish generative tasks. "NQII" is Natural Questions in Icelandic (NQiI,
arXiv 2603.16406), not a Danish task. ScandEval paper: Nielsen, NoDaLiDa 2023, arXiv 2304.00906
(fine-tuned encoders only; ScandiQA-da = MKQA questions with DeepL-translated NQ contexts, 6,311 /
749 / 750). Generative methodology: Nielsen et al., "Encoder vs Decoder", arXiv 2406.13469.

### 1.3 Other Danish and Nordic factual QA and cultural knowledge numbers

| Benchmark | Model | Size | Setting | Metric | Number | Citation | Comparable? |
|---|---|---|---|---|---|---|---|
| MultiWikiQA-da (5,000 LLM-generated Q/A from Danish Wikipedia, answer verbatim in article) | Mistral-Small-3.1-24B Base / Instruct | 24B | EuroEval few-shot, passage given | F1 | 78.9 +- 2.7 / 77.1 +- 2.3 | arXiv 2509.04111, Table 4 | Reading step only, hit guaranteed |
| same | Llama-3.1-8B base / Instruct | 8B | same | F1 | 75.2 +- 2.3 / 74.2 +- 2.0 | same | |
| same | XLM-RoBERTa-large / mE5-large fine-tuned | 560M | | F1 | 32.3 +- 3.9 / 33.1 +- 2.4 | same | |
| ScandiQA-da (translated NQ contexts) | SnakModel-7B-instruct | 7B | ScandEval, passage given | F1 | 64.66 | arXiv 2412.12956, Table 3 | Extractive, translated English trivia; not Danish knowledge |
| same | Munin-7B-alpha / Mistral-7B-v0.1 / Llama2-7B chat / Viking-7B | 7B | same | F1 | 63.44 / 64.55 / 61.34 / 56.29 | same, Table 3 | |
| Danske Talemaader (Table 3 accuracy, older dataset version) | Munin-7B-v0.1dev0 / Munin-7B-alpha / SnakModel-7B-instruct / Mistral-7B / Viking-7B | 7B | few-shot MCQ | acc | 93.45 / 83.01 / 71.05 / 64.50 / 23.97 | arXiv 2412.12956, Table 3 | MCQ; treat the 93.45 with care (munin-7b-alpha scores 46.32 acc on the current board) |
| Danish Citizen Tests (Table 3, older version) | Munin-7B-v0.1dev0 / SnakModel-7B-instruct / Mistral-7B / Llama2-7B base / Viking-7B | 7B | few-shot MCQ | acc | 85.82 / 71.88 / 71.56 / 57.05 / 34.90 | same, Table 3 | MCQ |
| Danoliteracy citizenship test (605 MCQ, chance 36) | Gemini Pro / GPT-3.5 Turbo / Mistral-7B-Instruct / Llama-2-7B / Dano.Llama-2-7B / dummy | | zero-shot | acc | 85 / 82 / 47 / 39 / 37 / 36 (each +- 1 to 2) | arXiv 2410.22839 (NoDaLiDa 2025), Table 2 | MCQ; 7B models near chance on Danish civic knowledge |
| Danoliteracy human A/B win rate over 8 scenarios | Claude Opus / GPT-4o / Llama-3-70B / Llama-3-8B-Instruct / DanskGPT-tiny Chat 1.1B | | | win % | 94 / 76 / 40 / 32 / 18 | same, Table 8 | "DanskGPT-tiny Chat ... fails on knowledge and understanding" |
| DaKultur (1,038 native-speaker cultural prompts) | SnakModel-7B-instruct / Llama2-7B chat+INSTda / Llama2-7B base+INSTda | 7B | open generation | acceptance % | 42.4 / 15.0 / 13.9 | arXiv 2504.02403, Table 1 | Open-ended, not EM |
| NorQuAD (Norwegian, 4,752 manual extractive pairs) | NB-BERT / XLM-R / mBERT / human | encoders | fine-tuned, passage given | EM / F1 | 69.68 / 81.27; 64.52 / 78.42; 63.32 / 76.00; 78.13 / 91.14 | arXiv 2305.01957 (NoDaLiDa 2023), Table 4 | Ceiling for passage-given Nordic extractive QA: EM 70 to 78 |
| MultiLoKo (500 locally sourced short-answer q per language, 31 languages, EM) | Gemini 2.0 Flash / Llama 3.1 405B / GPT-4o / Llama 3.1 70B base / Claude 3.5 Sonnet / Qwen2.5-72B | | closed-book, 5-shot base or 0-shot chat | avg EM | 34.39 / 34.31 / 33.97 / 26.92 / 26.89 / 19.66 | arXiv 2504.10356, Table 2 (dev) | Danish is NOT among the 31 languages (Swedish is); included as the closest closed-book local-knowledge EM benchmark: frontier models score about 34 EM |
| GPT-SW3 held-out Danish perplexity (char-normalised) | gpt-sw3 40B / 20B / 6.7B / 1.3B / 356M / 126M; GPT-NeoX-20B; Falcon-40B | | LM | ppl | 1.870 / 1.893 / 1.923 / 2.019 / 2.157 / 2.346; 2.338; 2.238 | arXiv 2305.12987, Table 6 | LM only; no Danish QA in the paper |
| Poro 34B | | 34B | | | no Danish evaluation (FIN-bench 66.28, Table 6) | arXiv 2404.01856 | none |
| Viking 7B / 13B / 33B | | | | | no numbers on the model cards; only the SnakModel Table 3 row and the EuroEval rows above | huggingface.co/LumiOpen | |

### 1.4 Danish retrieval and RAG evaluations

| Source | Setup | System | Metric | Number | Citation | Comparable? |
|---|---|---|---|---|---|---|
| Scandinavian Embedding Benchmark (SEB), Danish retrieval tasks TV2Nord (4,096 docs), Twitterhjerne (340), DanFEVER (8,897 wiki claims), nDCG@10 | zero-shot embeddings | text-embedding-3-large / embed-multilingual-v3.0 / text-embedding-3-small / multilingual-e5-large 560M / e5-mistral-7b / multilingual-e5-base / small / dfm-encoder-large | Retrieval avg (7 tasks, all languages) / Danish avg (12 tasks) | 77.9 / 63.7; 75.2 / 62.6; 71.3 / 59.7; 69.1 / 61.1; 66.0 / 61.7; 63.5 / 58.6; 60.3 / 56.5; 20.1 / 47.7 | arXiv 2406.02396 (NeurIPS 2024 D&B), Table 2 | Retriever side only, no reader EM; per-task Danish retrieval scores are on the SEB dashboard (UNVERIFIED here) |
| lex.dk production RAG ("The Coverage Illusion", Hussain and Nielbo, Aarhus CHC): 240,000 encyclopedia articles, 1,000 real user queries, LLM-judged composite (1 to 5) and coverage | retrieval variants | Semantic / Semantic+CE / Hybrid BM25+dense+RRF / QE+CE / HyDE / Oracle | composite overall / coverage % | 3.058 / 62.6; 3.086 / 62.8; 3.408 / 72.2; 3.601 / 77.9; 3.944 / 86.4 (96 s latency); 4.404 oracle | arXiv 2605.27220, Table 1 | Only Danish production RAG evaluation found; no EM. Their decomposition: coverage expansion +1.020 points, better synthesis +0.076, i.e. hit rate dominates, as in our ceiling analysis |
| Alexandra Institute, DFM, DTU, KU CoAStaL, ITU, Danske Bank, Novo Nordisk, Ordbogen "Danish RAG benchmark" or "Danish legal RAG" | | | | nothing published with EM or F1 as of 4 Sep 2026 | | none exists |

Small-versus-large gap on Danish factual knowledge, in one line each: DAISY closed-book EM on the
592: 1 to 4B general models 0.0 to 5.6 (Mimir report Table 9, our runs 0.8 to 5.6), Danish-specialised
1B 9.6, 8B 12.5, Llama 3.3 70B 22.5; EuroEval Citizen Tests accuracy: 1B 35 to 44, 3 to 4B 61 to 85,
70B 96, frontier 100; Talemaader accuracy: 1B 23 to 38, 3 to 4B 38 to 67, 27B 89, frontier 97 to 99;
MultiWikiQA-da EM with the passage given: 1B 0 to 66 (Mimir 66, Llama 3.2 1B 0), 3B 53, 70B 42,
best 70. With a gold passage the size gap closes; without it a 70B model keeps a 4x lead.

---

## 2. English entity-centric short-answer QA

### 2.1 PopQA (Mallen et al., "When Not to Trust Language Models", ACL 2023, arXiv 2212.10511)

Dataset: 14,282 questions from Wikidata triples over 16 relations (occupation, place of birth, genre,
father, country, producer, director, capital of, screenwriter, composer, color, religion, sport,
author, mother, capital), one template per relation ("Who was the director of [subj]?"); popularity
= Wikipedia monthly page views of the subject; gold = all Wikidata objects; metric acc(contains)
("any substring of the prediction is an exact match of any of the gold answers", Sec. 3.1). Prompt
"Q: ... A:", 15-shot for GPT-Neo/OPT, 0-shot for GPT-3. Retrieval: BM25 or Contriever (MS MARCO)
over Wikipedia Dec 2018, top-1 paragraph prepended. Also EntityQuestions (82 percent subset with a
unique Wikidata match). Per-model values exist only as bar charts (Figures 4, 7, 13, 14); text anchors:
GPT-3 davinci 35 percent vanilla, GPT-NeoX 20B 25 percent (Sec. 4.2), Contriever +7 points on
davinci-003 (Sec. 5.2), best adaptive 46.5 percent (Sec. 6.2).

| Model | Size | Vanilla | GenRead | BM25 top-1 | Contriever top-1 | EntityQuestions vanilla / Contriever | Source |
|---|---|---|---|---|---|---|---|
| GPT-Neo | 1.3B | 0.11 | 0.12 | 0.215 | 0.335 | 0.085 / 0.285 | Figs 13, 14, read from figure |
| OPT | 1.3B | 0.12 | 0.12 | 0.22 | 0.34 | | Fig 13 |
| GPT-Neo | 2.7B | 0.125 | 0.135 | 0.23 | 0.355 | 0.10 / 0.305 | Figs 13, 14 |
| OPT | 2.7B | 0.125 | 0.135 | 0.235 | 0.36 | | Fig 13 |
| GPT-J | 6B | 0.16 | 0.17 | 0.245 | 0.37 | 0.12 / 0.32 | Figs 13, 14 |
| OPT | 6.7B | 0.155 | 0.17 | 0.25 | 0.37 | | Fig 13 |
| OPT | 13B | 0.175 | 0.185 | 0.255 | 0.375 | 0.13 / 0.33 | Figs 13, 14 |
| GPT-NeoX | 20B | 0.20 (text: 25) | | 0.255 | 0.38 | 0.135 / 0.325 | Figs 13, 14, Sec 4.2 |
| GPT-3 davinci-002 | 175B | 0.345 | 0.365 | 0.335 | 0.41 | | Fig 13 |
| GPT-3 davinci-003 | 175B | 0.34 (text: 35) | 0.39 | 0.32 | 0.41 | 0.245 / 0.35 (BM25 0.36) | Figs 13, 14 |

Long-tail findings: scaling raises accuracy only for log10(page views) above about 4; the most
popular bucket goes from about 0.45 (1.3B) to 0.70 (20B) to 0.78 (GPT-3) while the 10^2 to 10^3
buckets stay at 0.05 to 0.15 at every size (Fig 5, read from figure); on the 4,000 least popular
questions GPT-J 6B / NeoX 20B / davinci-003 score 15 / 16 / 19 percent (Sec 4); retrieval flips 10
percent of davinci-003's correct answers to wrong (Contriever recall@1 0.14 on those, 0.42 overall)
and 17 percent wrong to correct (recall@1 0.88) (Table 1); "a much smaller LM (GPT-Neo 2.7B)
augmented by the Contriever retrieval results outperforms vanilla GPT-3" (Sec 5.2). Adaptive
retrieval (retrieve only when subject popularity is below a per-relation threshold): davinci-003
adaptive with GenRead + Contriever 46.5, 5.3 points above any non-adaptive method; davinci-003 with
BM25 retrieves on 40 percent of questions; models under 10B "almost always retrieve" so the gain is
"much smaller" (Sec 6.2, Figs 9, 10); latency cut up to 9 percent and GPT-3 API cost about halved
on PopQA, 15 percent API saving on EntityQuestions (Figs 11, 12). API cost per 1000 questions: $0.46
vanilla, $2.80 BM25, $3.08 Contriever, $3.25 GenRead (App. B).

Comparability: the closest English analogue to DAISY (one subject, one relation, short answer, long
tail). Two differences inflate PopQA relative to us: acc(contains) versus strict EM, and multi-alias
gold sets. Our shaped-query hit rate (0.404 gold-in-top-3) is close to their Contriever recall@1
(0.42), and our retrieve EM band (0.15 to 0.31) sits just under their Contriever band (0.335 to 0.38
for 1.3B to 20B), which is what strict EM against a single gold string should cost.

### 2.2 Closed-book TriviaQA and Natural Questions for small models (official cards and papers)

| Model | Size | Benchmark | Setting | Metric | Number | Citation | Comparable? |
|---|---|---|---|---|---|---|---|
| Gemma 3 1B / 4B / 12B / 27B (pre-trained) | | TriviaQA | 5-shot | acc | 39.8 / 65.8 / 78.2 / 85.5 | arXiv 2503.19786, Table 9 (scoring in Table 19) | Only vendor number for a model we ran (4B: 65.8) |
| same | | Natural Questions | 5-shot | acc | 9.48 / 20.0 / 31.4 / 36.1 | same | NQ is the shorter, more entity-centric set |
| Gemma 2 2B / 9B / 27B | | TriviaQA / NQ | 5-shot | acc | 60.4 / 17.1; 76.6 / 29.2; 83.7 / 34.5 | arXiv 2408.00118, Table 13 | |
| Gemma 1 2B / 7B | | TriviaQA / NQ | 5-shot | acc | 53.2 / 12.5; 63.4 / 23.0 | arXiv 2403.08295, Table 6 | |
| Llama 3.2 3B base | 3.2B | NQ / TriviaQA / PopQA | 0-shot direct answer | strict EM | 16.20 / 29.60 / 7.40 | arXiv 2505.04588v3 (ZeroSearch), Table 3 | Same model family as ours, strict EM |
| Qwen 2.5 3B base | 3.1B | NQ / TriviaQA / PopQA | 0-shot direct | strict EM | 12.40 / 30.60 / 5.60 | same | |
| Qwen 2.5 3B Instruct | 3.1B | NQ / TriviaQA / PopQA | 0-shot direct inference | strict EM | 10.6 / 28.8 / 10.8 | arXiv 2503.09516 (Search-R1, COLM 2025), Table 2 | Same model as ours |
| Qwen 2.5 7B Instruct | 7B | NQ / TriviaQA / PopQA | same | strict EM | 13.4 / 40.8 / 14.0 | same | |
| Llama 3.2 1B / 3B; Qwen 2.5 1.5B / 3B; SmolLM2 1.7B; gemma-2-2b; Llama 3.1 8B; gemma-2-9b; OLMo-2-32B (base) | | TriviaQA | lm-eval-harness 0-shot, no evidence | EM | 0.2509 / 0.5088; 0.2942 / 0.4242; 0.3879; 0.5080; 0.6170; 0.6803; 0.7356 | arXiv 2509.02225, Table 6 | Reproducible with a 6 GB GPU |
| SmolLM2 1.7B / Llama 3.2 1B / Qwen 2.5 1.5B (base) | | TriviaQA / NQ | lighteval | metric not stated (UNVERIFIED whether EM or quasi-EM) | 36.7 / 8.7; 28.1 / 6.2; 20.9 / 10.5 | arXiv 2502.02737, Table 4 | |
| Phi-3-mini | 3.8B | TriviaQA | 5-shot | acc | 64.0 (phi-2 45.2, Mistral 7B 75.2, Llama-3-8B-inst 67.7, GPT-3.5 85.8) | arXiv 2404.14219, Sec. 3 table | Paper admits "low performance on TriviaQA" from limited capacity for facts |
| Phi-4-mini, Qwen2.5 report, MiniCPM, Llama 3.2 model cards, Llama 3 paper | | TriviaQA / NQ | | | not reported (checked arXiv 2503.01743, 2412.15115, 2404.06395, 2407.21783, Meta HF cards) | | none |
| Mistral 7B | 7B | TriviaQA / NQ | 5-shot, no context | acc | 69.9 / 28.8 (Llama 2 7B 63.8 / 24.7, 13B 69.6 / 29.0) | arXiv 2310.06825, Table 2 | |
| LLaMA 1 7B / 13B / 65B | | NQ | 0 / 5 / 64-shot | acc(contains) per RA-DIT footnote 7 | 16.8 / 22.0 / 26.1; 20.1 / 28.1 / 31.9; 23.8 / 35.0 / 39.9 | arXiv 2302.13971, Table 4 | |
| LLaMA 1 7B / 65B | | TriviaQA filtered dev | 0 / 5 / 64-shot | same | 50.0 / 56.3 / 57.6; 68.2 / 72.6 / 73.0 | same, Table 5 | |
| Llama 65B | 65B | NQ / TriviaQA | 0-shot, strict EM | EM | 5.2 / 55.8 (5-shot 31.6 / 71.8) | arXiv 2310.01352 (RA-DIT), Table 2 and footnote 7 | Strict 0-shot EM is near floor even at 65B; the same effect that keeps our 70B at 22.5 |
| Llama 3.1 70B base | 70B | TriviaQA-Wiki | 5-shot | EM | 89.8 (Llama 3 70B 89.7; 405B 91.8; 8B 77.6) | Meta model card, huggingface.co/meta-llama/Llama-3.1-70B-Instruct | Llama 3.3 70B has no published TriviaQA/NQ; it is a post-training refresh of this base |
| Llama 3.1 70B / 8B base; Gemma 3 27B | | NQ / TriviaQA | 5-shot, OLMES | F1 | 51.3 / 92.2; 33.9 / 80.3; 45.4 / 89.1 | arXiv 2501.00656 (OLMo 2), Table 6 | |
| Gopher family 44M / 117M / 417M / 1B / 7.1B / 280B; GPT-3 175B | | NQ | 0-shot / 64-shot prompted | acc | 0.0 / 0.8; 0.1 / 1.8; 0.4 / 3.4; 2.4 / 8.1; 6.1 / 16.5; 10.1 / 28.2; 14.6 / 29.9 | arXiv 2112.11446, Table A15 | The canonical prompted closed-book size curve: a 1B model scores 2.4 0-shot on NQ |
| same | | TriviaQA | 0-shot / 64-shot | acc | 0.1 / 1.0; 0.3 / 3.8; 0.7 / 8.6; 6.5 / 18.8; 19.9 / 36.1; blank / 57.2; 64.2 / 71.2 | same | |
| T5 closed-book fine-tuned Base / Large / 3B / 11B / 11B+SSM | 220M to 11B | NQ / WQ / TriviaQA-Wiki test | fine-tuned | EM | 25.9 / 27.9 / 29.1; 28.5 / 30.6 / 35.9; 30.4 / 33.6 / 43.4; 32.6 / 37.2 / 50.1; 34.8 / 40.8 / 60.5 | arXiv 2002.08910 (Roberts et al., EMNLP 2020), Table 1 | Fine-tuned; the "how much knowledge fits in parameters" curve |
| SimpleQA closed-book (English, LLM-graded) | Gemma 3 1B / 4B / 12B / 27B IT | | 0-shot | correct % | 2.2 / 4.0 / 6.3 / 10.0 | arXiv 2503.19786, Table 6 | Our Gemma 3 4B closed-book DAISY 5.6 EM; same floor |
| SimpleQA closed-book | Llama-3.3-70B / Qwen2.5-72B / GPT-4o-mini / phi-4 14B / GPT-4o | | | correct % | 20.9 / 10.2 / 9.9 / 3.0 / 39.4 | arXiv 2412.08905 (phi-4), Table 1 | Llama 3.3 70B on SimpleQA (20.9) versus on DAISY (22.5): the canon is about as hard for it as SimpleQA |

### 2.3 Retrieval-augmented TriviaQA, NQ and PopQA for 1B to 8B models (single retrieval unless stated)

| Paper | Model | Size | Retrieval | Metric | No retrieval | With retrieval | Delta | Citation | Comparable? |
|---|---|---|---|---|---|---|---|---|---|
| Search-R1 | Qwen2.5-3B-Instruct | 3B | E5, Wikipedia 2018, top-3, question as query | strict EM | NQ 0.106 / TQA 0.288 / PopQA 0.108 | RAG 0.348 / 0.544 / 0.387 | +24.2 / +25.6 / +27.9 | arXiv 2503.09516, Table 2 | Closest published analogue of DAISY retrieve: same model, one call, strict EM |
| Search-R1 | Qwen2.5-7B-Instruct | 7B | same | EM | 0.134 / 0.408 / 0.140 | RAG 0.349 / 0.585 / 0.392 | +21.5 / +17.7 / +25.2 | same | |
| ZeroSearch | Llama-3.2-3B base | 3B | Google via SerpAPI, 5 docs | EM | 16.20 / 29.60 / 7.40 | RAG 30.00 / 57.60 / 26.40 | +13.8 / +28.0 / +19.0 | arXiv 2505.04588v3, Table 3 | Web search, not Wikipedia |
| ZeroSearch | Qwen-2.5-3B base | 3B | same | EM | 12.40 / 30.60 / 5.60 | RAG 31.60 / 58.00 / 15.20 | +19.2 / +27.4 / +9.6 | same | |
| ZeroSearch | Qwen-2.5-7B base | 7B | same | EM | 11.60 / 35.60 / 1.20 | RAG 27.40 / 58.20 / 17.80 | | same | |
| Adaptive-RAG | FLAN-T5-XL | 3B | BM25, Wikipedia (DPR dump), 500 q per set | EM (F1, Acc) | NQ 14.20 (19.00, 15.60) / TQA 25.00 (31.80, 27.00) / SQuAD 3.60 | single-step 37.80 (47.30, 44.60) / 53.60 (62.40, 60.20) / 27.80 | +23.6 / +28.6 / +24.2 | arXiv 2403.14403 (NAACL 2024), Table 2 | 3B, one BM25 call, strict EM, Step = 1.00, Time = 1.00: the best-matched cost row |
| Adaptive-RAG | FLAN-T5-XXL | 11B | same | EM | 18.80 / 32.80 / 7.00 | 41.40 / 56.00 / 28.80 | | same, Table 7 | |
| Adaptive-RAG | GPT-3.5 Turbo | | same | EM | NQ 39.80 / TQA 64.00 | 32.40 / 55.20 | retrieval hurts | same, Table 8 | The strong closed-book regime, opposite of ours |
| Probing-RAG | Gemma-2B | 2B | BM25, Adaptive-RAG corpus, 500 q | EM (Acc) | NQ 15.0 (24.6) / TQA 37.4 (45.4) / HotpotQA 16.8 | single-step 11.4 (26.0) / 19.6 (38.8) / 14.6 | retrieval HURTS by 3.6 / 17.8 / 2.2 | arXiv 2410.13339 (NAACL 2025 Findings), Table 1 | The only sub-3B adaptive-retrieval datapoint; distraction dominates at 2B with BM25 |
| Probing-RAG | Gemma-2B | 2B | prober-gated (0.80 calls per q) | EM | | Probing-RAG 21.6 / 41.8 / 21.8 | | same, Tables 1, 2 | |
| In-context RALM | LLaMA-7B / 13B / 33B | | DPR top-2, frozen LM, 0-shot | EM | NQ 10.3 / 12.0 / 13.7; TQA 47.5 / 54.8 / 58.3 | 28.0 / 31.0 / 32.3; 56.0 / 60.1 / 62.7 | +17.7 / +19.0 / +18.6 | arXiv 2302.00083 (TACL 2023), Table 4 | Frozen LM, prepended passages, strict EM: the same mechanism as ours |
| Self-RAG baselines | Llama2-7B / 13B | | Contriever-MS MARCO top-5 Wikipedia (2020 dump for PopQA) plus 5 web docs; PopQA long-tail 1,399 q (< 100 monthly views); TQA unfiltered 11,313 | acc(contains) | PopQA 14.7 / 14.7; TQA 30.5 / 38.5 | 38.2 / 45.7; 42.5 / 47.0 | +23.5 / +31.0; +12.0 / +8.5 | arXiv 2310.11511 (ICLR 2024), Table 2 | Long-tail entity questions, untrained base models with passages: the shape of our retrieve gain |
| Self-RAG baselines | Alpaca-7B / 13B; Llama2-chat-13B; ChatGPT | | same | acc(contains) | PopQA 23.6 / 24.4 / 20.0 / 29.3; TQA 54.5 / 61.3 / 59.3 / 74.3 | 46.7 / 46.1 / 51.8 / 50.8; 64.1 / 66.9 / 59.8 / 65.7 | | same | Retrieval hurts ChatGPT on TQA (74.3 to 65.7) |
| Self-RAG | Self-RAG 7B / 13B (trained) | | same | acc(contains) | | PopQA 54.9 / 55.8; TQA 66.4 / 69.3 | | same | |
| CRAG | LLaMA2-hf-7b; SelfRAG-LLaMA2-7b | 7B | Self-RAG's top-10 Contriever input, T5-large evaluator, Google web search top-5 on doubtful cases | acc(contains) | | PopQA RAG 50.5 / 52.8; CRAG 54.9 / 59.8; Self-CRAG 49.0 / 61.8 | | arXiv 2401.15884, Table 1 | Web-search fallback is the analogue of a second query |
| Speculative RAG | Mistral-7B / Mistral-Instruct-7B / Mixtral-Instruct-8x7B standard RAG; drafter 7B + verifier 8x7B | | Contriever top-10 (15 MuSiQue), 5 drafts of 2 docs | acc | | TriviaQA 54.15 / 67.11 / 73.91 / 74.24; PopQA 31.38 / 42.17 / 53.68 / 57.54 | | arXiv 2407.08223, Table 1 | latency 1.17 to 1.93 s per query on A100s |
| CtrlA | Mistral-7B | 7B | BM25 and BGE over Wikipedia 2018 plus web | acc(contains) | TQA 53.8 / PopQA 25.7 | SR-RAG 62.7 / 51.9; FLARE 72.4 / 48.3; CtrlA 76.4 / 61.8 | | arXiv 2405.18727 (ACL 2025 Findings), Table 1 | |
| RECOMP | Flan-UL2 20B | 20B | Contriever, Wikipedia Dec 2018 | EM | NQ 21.99 / TQA 49.33 | top-1 33.07 / 57.84; top-5 39.39 / 62.37 | +17.4 / +13.0 (top-5) | arXiv 2310.04408 (ICLR 2024), Table 2 | |
| Chain-of-Note | LLaMA-2 7B fine-tuned | 7B | DPR top-5 | EM | NQ 28.80 / TQA 63.19 / WebQ 28.30 | Retrieve-Read 47.39 / 74.92 / 29.58; +CoN 48.92 / 76.27 / 32.33 | +18.6 / +11.7 | arXiv 2311.09210, Table 2 | Fine-tuned reader |
| FlashRAG | Llama3-8B-instruct | 8B | e5-base-v2 top-5, Wikipedia Dec 2018 | EM | NQ 22.6 / TQA 55.7 / PopQA 21.7 | Standard RAG 35.1 / 58.8 / 36.7; best (Ret-Robust) 42.9 / 68.2 / 57.2 | +12.5 / +3.1 / +15.0 | arXiv 2405.13576, Table 3 | The reference toolkit; index files are large (see Sec. 8) |
| Adapt-LLM | Llama-2-7B fine-tuned to emit RET | 7B | Contriever best passage, PopQA 14,282 | EM | Never 21.43 | Always 35.86; Adapt-LLM 36.77 (retrieves on 82 percent) | +14.4 | arXiv 2404.19705, Tables 1, 3 | Gold passage 89.42 vs Contriever best passage 22.49 on SQuAD dev (Table 4): the oracle-versus-real gap |
| SmartRAG | Flan-T5-large 780M; Llama-2-7B | | Bing top-4 snippets | EM | PopQA 7.03; 21.79 | Vanilla RAG 34.36; 32.26; SmartRAG 42.50; 44.32 | +27.3; +10.5 | arXiv 2410.18141 (ICLR 2025), Table 1 | A 780M model with web snippets reaches 34 to 42 on PopQA |
| Parametric RAG | LLaMA-3.2-1B-Instruct; Qwen2.5-1.5B-Instruct | 1B; 1.5B | BM25 top-3, 300 q per set | F1 | | Standard RAG PopQA 0.1839; 0.0999; FLARE 0.1301; 0.0641; DRAGIN 0.1056; 0.0548; P-RAG 0.2205; 0.1885 | | arXiv 2501.15915 (SIGIR 2025), Table 1 | The only paper with 1B and 1.5B models on PopQA: iterative methods collapse below 8B |
| Can Small LMs Use What They Retrieve | SmolLM2-360M; Qwen2.5-1.5B / 3B / 7B (NF4 4-bit); Llama-3.1-8B | | 500K-passage Wikipedia subset (hit@5: BM25 10.5 percent, E5 16.3 percent), oracle passages | EM | pilot None 1.5 / 14.5 / 19.5 / 16.5 | Dense 0.0 / 3.5 / 12.0 / 14.0; on unknown questions with the oracle passage 0.0 / 10.0 / 12.8 / 14.6; net change from dense retrieval minus 1.3 to minus 2.9 pp | negative | arXiv 2603.11513, Tables 3, 4 | Same size and quantisation class as ours, opposite sign; the corpus covers 2 percent of Wikipedia, so hits are rare and distraction wins |
| RetrievalQA (1,271 q that need retrieval) | TinyLlama 1.1B / Llama-2-7B-chat / GPT-3.5 / GPT-4 | | top-5 passages or Google | match acc | 4.2 / 2.0 / 1.2 (Table 6) | 28.2 / 36.0 / 38.2 / 46.0 (Table 1) | +24 / +34 / +37 | arXiv 2402.16457 | Long-tail plus post-cutoff; a 1.1B model goes from 4 to 28 |
| Lost in the Middle | GPT-3.5-Turbo / Claude-1.3 | | NQ-Open 2,655 q, oracle passage only | acc(contains) | 56.1 / 48.3 | oracle 88.3 / 76.1 | +32.2 / +27.8 | arXiv 2307.03172 (TACL 2024), Table 1 | Oracle-passage reference for our retrieve-oracle |
| B1ade | Llama-3.2-1B; Qwen-2.5-1.5B; B1ade-1B | 1B | top-5 passages, corpus and hit rate not stated | EM | | PopQA 48.55 / 74.77 / 81.82; TQA 36.65 / 41.10 / 33.11; NQ 35.67 / 51.36 / 48.32 | | arXiv 2607.27506, Table 2 | Setup underspecified: UNVERIFIED for comparison |
| Gemma 3 4B, Phi-3 / Phi-4-mini with and without retrieval on PopQA / NQ / TriviaQA | | | | | not found in any paper | | none published |

### 2.4 Adaptive and agentic retrieval papers: main tables with model size and retrieval-call counts

Reading key: "no retrieval" = our closed-book; "single / always" = our retrieve (RC 1.0, LMC 1);
"adaptive" = decides per question; RL search agents write their own queries over several turns.
Only the Adaptive-RAG "EM", DRAGIN, Search-R1, ZeroSearch, SEAKR, Probing-RAG and TARG numbers are
strict EM like ours; Self-RAG, CRAG, UAR, Moskvoretskii "InAcc" and FLARE ASQA are containment.

| Paper (venue) | Model | Size | Datasets and retrieval | No retrieval | Always retrieve | Proposed method | Cost columns and headline | Table | Comparable? |
|---|---|---|---|---|---|---|---|---|---|
| Self-RAG, arXiv 2310.11511 (ICLR 2024) | Llama2 7B / 13B; Self-RAG 7B / 13B | 7B, 13B | PopQA long-tail 1,399, TQA 11,313, Contriever top-5 plus web; acc(contains) | PopQA 14.7 / 14.7; TQA 30.5 / 38.5 | 38.2 / 45.7; 42.5 / 47.0 | Self-RAG 54.9 / 55.8; 66.4 / 69.3 | retrieval frequency vs threshold delta only as Figure 3(c); training 4x A100, 145,619 instances; no per-query cost | Table 2 | Long-tail entity QA; the untrained "with retrieval" rows are our retrieve condition at 7B |
| FLARE, arXiv 2305.06983 (EMNLP 2023) | text-davinci-003 | 175B | 2WikiMultihopQA 500 (BM25 top-2), StrategyQA 229, ASQA 500, WikiAsp 500 (Bing) | 2Wiki EM 28.2 / F1 36.8; StrategyQA 72.9; ASQA EM 33.8 | single-time 39.4 / 48.8; 68.6; 40.0 | FLARE 51.0 / 59.7; 77.3; 41.3 | percent of sentences that trigger retrieval, 30 to 60 percent on average (App. A); performance plateaus above 60 percent on 2Wiki, drops above 50 percent on StrategyQA (Fig 5); no call counts, latency or dollars | Tables 1, 2 | Multi-hop, 175B; single retrieval hurts StrategyQA (72.9 to 68.6) |
| Adaptive-RAG, arXiv 2403.14403 (NAACL 2024) | FLAN-T5-XL | 3B | SQuAD, NQ, TriviaQA, MuSiQue, HotpotQA, 2Wiki; BM25; 500 q each; average over six | EM 14.87 / F1 21.12 / Acc 15.97; Step 0.00; Time 0.11 | single-step 34.83 / 44.31 / 38.87; Step 1.00; Time 1.00 | Adaptive-RAG 37.17 / 46.94 / 42.10; Step 2.17; Time 3.60. Adaptive Retrieval (Mallen) 23.87; Step 0.50; Time 0.56. Self-RAG 7B 9.90 EM; Step 0.72. Multi-step IRCoT 39.00; Step 4.69; Time 8.81. Oracle classifier 45.00; Step 1.28 | Step = retrieve-and-generate iterations per query; Time relative to single-step; absolute per-query time by class: no retrieval 0.35 s (8.6 percent of queries), one-step 3.08 s (53.3 percent), multi-step 27.18 s (38.1 percent) (Table 3); classifier accuracy 54.52 (Table 4) | Tables 1, 2, 3 | THE cost-accounting reference; the 3B single-step row is our retrieve condition in English |
| same | FLAN-T5-XXL; GPT-3.5 | 11B; API | same | 17.83 EM; 35.77 EM | 37.87; 34.73 | 38.90 (Step 1.35); 37.97 (Step 1.03) | GPT-3.5 no-retrieval NQ 39.80 and TQA 64.00 beat single-step 32.40 and 55.20 (Table 8) | Tables 1, 7, 8 | Strong closed-book models lose from always-retrieve |
| DRAGIN, arXiv 2403.10081 (ACL 2024) | Llama2-7B-chat / 13B-chat; Vicuna-13B | 7B, 13B | 2Wiki, HotpotQA, StrategyQA, IIRC; BM25 top-3; 1000 q | 7B: 2Wiki EM 0.146, HotpotQA 0.184; 13B: 0.187, 0.223 | SR-RAG 7B 0.169, 0.164 (single retrieval lowers HotpotQA); 13B 0.245, 0.263 | DRAGIN 7B 0.220, 0.232; 13B 0.304, 0.314; FLARE 7B 0.143, 0.149 | #Num = retrieval calls per question: FL-RAG 3.3 to 4.2, FS-RAG 3.1 to 6.8, FLARE 0.3 to 5.5, DRAGIN 2.5 to 4.8 (Table 3); no latency | Tables 2, 3 | Multi-hop; dynamic methods cost 3 to 5 calls per question for +3 to +8 EM |
| CRAG, arXiv 2401.15884 | LLaMA2-7b; SelfRAG-7b | 7B | PopQA 1,399, Bio, PubHealth, ARC; T5-large evaluator; web search top-5 on doubtful cases | (Self-RAG rows) | RAG 50.5 / 52.8 PopQA | CRAG 54.9 / 59.8; Self-CRAG 49.0 / 61.8 | TFLOPs per token and seconds per instance (generation only): RAG 26.5 / 0.363 s; CRAG 27.2 / 0.512 s; Self-RAG up to 132.4 / 0.741 s; Self-CRAG 0.908 s (Table 6); evaluator accuracy 84.3 vs ChatGPT 58.0 to 64.7 (Table 4) | Tables 1, 4, 6 | Web fallback = second query |
| Speculative RAG, arXiv 2407.08223 (Google) | Mistral-7B drafter, Mixtral-8x7B verifier | 7B + 47B | TriviaQA, MuSiQue, PopQA, PubHealth, ARC; Contriever top-10, 5 drafts of 2 docs | | standard RAG Mixtral-Instruct 73.91 TQA / 53.68 PopQA | 74.24 / 57.54 | wall-clock only: 1.93 s per query TQA, 1.17 s PubHealth (Table 2); latency reduced 11.9 to 50.8 percent vs standard RAG 8x7B (Fig 3); always one retrieval | Tables 1, 2 | Not transferable to a GTX 1060 |
| Mallen adaptive retrieval, arXiv 2212.10511 | GPT-Neo 2.7B / GPT-J 6B / NeoX 20B / davinci-003 | | PopQA, BM25 or Contriever top-1 | 0.12 / 0.16 / 0.20 / 0.34 | BM25 0.225 / 0.25 / 0.255 / 0.315 | adaptive 0.235 / 0.26 / 0.285 / 0.40 (best 46.5 with GenRead + Contriever) | fraction of questions retrieving: davinci-003 40 percent (BM25); NeoX 20B 75 to 80 percent; models under 10B "almost always retrieve"; latency minus 9 percent; API cost halved | Figs 9 to 12, Sec 6.2 | The popularity gate collapses to always-retrieve at our size |
| Search-R1, arXiv 2503.09516 (COLM 2025) | Qwen2.5-3B / 7B base and instruct | 3B, 7B | NQ, TriviaQA, PopQA, HotpotQA, 2Wiki, MuSiQue, Bamboogle; E5 top-3 Wikipedia 2018; up to 4 search turns; trained on NQ + HotpotQA; strict EM | 3B-inst direct NQ 0.106 / TQA 0.288 / PopQA 0.108 (7-set avg 0.134) | RAG 0.348 / 0.544 / 0.387 (avg 0.270) | Search-R1-instruct 3B 0.341 / 0.545 / 0.378 (avg 0.325); Search-R1-base 3B 0.406 / 0.587 / 0.435 (avg 0.303); 7B-base 0.480 / 0.638 / 0.457 (avg 0.431); IRCoT 3B 0.111 / 0.312 / 0.200; Search-o1 3B 0.238 / 0.472 / 0.262 | training 8x H100, 500 PPO steps; "# valid search" only as a training curve (Fig 2d); no per-query inference count; top-k study 7B: top-1 avg 0.375, top-3 0.431, top-5 0.400 (Table 7) | Tables 2, 5, 7 | Same 3B model as ours; on the three single-hop sets the RL agent is level with plain one-call RAG (0.341 vs 0.348 NQ) |
| ZeroSearch, arXiv 2505.04588v3 | Qwen-2.5-3B; LLaMA-3.2-3B (base and instruct) | 3B | same seven sets; Google via SerpAPI, 5 docs at evaluation; EM; test sizes not stated | Qwen 12.40 / 30.60 / 5.60; Llama 16.20 / 29.60 / 7.40 | RAG Qwen 31.60 / 58.00 / 15.20; Llama 30.00 / 57.60 / 26.40 | Search-R1-base Qwen 40.60 / 60.00 / 44.20, Llama 41.20 / 60.00 / 44.00; ZeroSearch-base Qwen 43.00 / 61.60 / 41.40, Llama 43.40 / 63.80 / 48.40; ZeroSearch-inst Qwen 41.40 / 57.40 / 44.80, Llama 40.20 / 58.00 / 46.00; RAgent Qwen 15.20 / 28.40 / 6.60 | training-time search cost only: Google $586.7 per about 64k queries vs simulated engine $17.7 (3B, 1x A100) to $70.8 (14B) (Table 8) | Tables 3, 8 | Untrained "RAgent" (prompted agent) at 3B is BELOW plain RAG; RL lifts it 10 to 30 points |
| R1-Searcher, arXiv 2503.05592 | Llama-3.1-8B-Instruct; Qwen-2.5-7B-Base | 8B, 7B | HotpotQA, 2Wiki, Bamboogle, MuSiQue; BGE over KILT Wikipedia; Cover-EM / LLM-judge | naive 0.208 / 0.326 / 0.144 / 0.068 (Llama) | standard RAG 0.334 / 0.336 / 0.168 / 0.104 | R1-Searcher 0.648 / 0.594 / 0.504 / 0.254 (Llama); 0.654 / 0.636 / 0.528 / 0.282 (Qwen) | retrieval counts only as training curves | Table 2 | Multi-hop, 7 to 8B |
| ReSearch, arXiv 2503.19470 | Qwen2.5-7B-Instruct | 7B | HotpotQA 7,405, 2Wiki 12,576, MuSiQue 2,417, Bamboogle 125; E5 top-5 | naive 19.18 / 25.76 / 3.76 / 10.40 EM | naive RAG 31.90 / 25.78 / 6.21 / 20.80 | ReSearch 43.52 / 47.59 / 22.30 / 42.40 | 64x H800; no per-query count | Table 2 | Multi-hop |
| Search-o1, arXiv 2501.05366 | QwQ-32B | 32B | NQ, TQA, HotpotQA, 2Wiki, MuSiQue, Bamboogle; Bing top-10 | NQ 23.0 / TQA 53.8 EM | RAG 29.6 / 65.6 | Search-o1 34.0 / 63.4; RAgent 33.6 / 62.0 | none | Table 3 | 32B reasoning model |
| SEAKR, arXiv 2406.19215 | LLaMA-2-7B-chat; LLaMA-3-8B-Instruct | 7B, 8B | 2Wiki, HotpotQA, IIRC, NQ 3,610, TQA 11,313, SQuAD 7,357; BM25 top-3; 20 samples for uncertainty | CoT NQ 13.4 / TQA 42.6 / SQuAD 8.7 EM | (not reported) | SEAKR 25.6 / 54.4 / 27.1; DRAGIN 23.2 / 54.0 / 18.7; FLARE 25.3 / 51.5 / 19.4; Self-RAG 32.3 / 21.2 / 5.1 | none in paper; reimplementation gives LMC 14.6, RC 1.00 (Moskvoretskii Table 1) | Tables 1, 2, 4 | Uncertainty from 20 samples per step: too expensive on a 1060 |
| UAR, arXiv 2406.12534 | Llama2-chat 7B / 13B | 7B, 13B | TriviaQA, WebQuestions, FreshQA and more; Contriever top-5 | TQA Never 62.15 / 63.18 | Always 68.73 / 71.02 (100 percent) | UAR 69.02 (50.1 percent retrieval) / 71.71 (48.5 percent); SKR 65.39 (48.9); FLARE 65.98 (58.8); Self-RAG 61.68 (53.5) | retrieval ratio (percent of queries) | Table 3 | Half the calls at equal accuracy, but only where closed-book is already 62 |
| SKR, arXiv 2310.05002 (EMNLP 2023 Findings) | text-davinci-003; ChatGPT | 175B, API | Temporal, Commonsense, Tabular, Strategy, Truthful; DPR top-3, 4-shot CoT | Manual-CoT avg 65.48; 67.89 | Manual-CoT-IR 66.36; 67.77 | SKR-knn 68.15; 70.62 | none quantified | Table 1 | Selective retrieval beats always by 2 to 3 points at 175B |
| Adapt-LLM, arXiv 2404.19705 | Llama-2-7B fine-tuned on NQ or SQuAD | 7B | PopQA 14,282, Contriever best passage, EM | Never 21.43 / 21.22 | Always 35.86 / 36.59 | Adapt-LLM 36.77 / 38.15 | RET emitted on 82.26 / 83.93 percent of PopQA (Table 3); popularity gate 99.86 percent, 36.81 acc (Table 5) | Tables 1, 3, 5 | A 7B model still asks on more than 80 percent of PopQA |
| Probing-RAG, arXiv 2410.13339 (NAACL 2025 Findings) | Gemma-2B; Mistral-7B | 2B, 7B | HotpotQA, NQ, TriviaQA, MuSiQue, 2Wiki; BM25; 500 q each | Gemma avg EM 19.0 / Acc 29.2 | single-step 14.0 / 27.4 | Probing-RAG 22.8 / 35.8; DRAGIN 22.4 / 25.1; FLARE 11.8 / 21.3; Adaptive-RAG 14.0 / 26.8 | total retrieval calls over 2,500 q: LLM-based 2,345; FLARE 5,317; DRAGIN 13,570; Adaptive-RAG 3,068; Probing-RAG 1,988 (0.80 per q; 57.5 percent no retrieval) (Table 2) | Tables 1, 2 | The one sub-3B adaptive datapoint: BM25 single-step hurts Gemma-2B on 4 of 5 sets |
| CtrlA, arXiv 2405.18727 (ACL 2025 Findings) | Mistral-7B | 7B | TQA 11,313, PopQA 1,399 (acc); 2Wiki, HotpotQA (EM) | TQA 53.8 / PopQA 25.7; 2Wiki EM 14.6 | SR-RAG 62.7 / 51.9; 16.9 (RC 1.00) | CtrlA 76.4 / 61.8; 36.9 (RC 2.01); DRAGIN 22.4 (RC 2.84) | retrieval frequency per question (Table 3) | Tables 1, 3, 11 | |
| Rowen, arXiv 2402.10612 (SIGIR-AP 2025) | GPT-3.5-turbo | API | TruthfulQA, StrategyQA 500, NQ, TQA; Serper Google | ChatGPT 47.92 / 61.40 | | Rowen-Hybrid 59.34 / 75.60; NQ 39.98 / TQA 69.04 EM (FLARE 32.50 / 59.00; Adaptive-RAG 35.04 / 58.00) | LLM calls per question 5 to 8; retrieval calls 0.5 to 1.5; retrieval ratio 20 to 23 percent (Tables 5, 9, 10) | Tables 4, 6, 9, 10 | |
| DioR, arXiv 2504.10198 (ACL 2025) | LLaMA2-7B-chat | 7B | 2Wiki, HotpotQA, IIRC, NQ, TQA, SQuAD; BM25 top-3; 1000 q | wo-RAG 2Wiki 0.146 EM; CoT NQ 13.4 / TQA 52.3 | SR-RAG 0.169 | DioR 0.266; NQ 26.2 / TQA 52.3 / SQuAD 21.5 | retrieval count 3.0, generation count 3.0, tokens 392 to 773 per question (Table 4) | Tables 2, 4, 5 | |
| TARG, arXiv 2511.09803 | Qwen2.5-7B-Instruct; Llama-3.1-8B-Instruct | 7B, 8B | TriviaQA, PopQA, NQ-Open; E5 / BGE-M3 | Never TQA 60.8 / PopQA 20.0 / NQ 38.8 (Qwen); 80.8 / 35.2 / 53.8 (Llama) | Always 57.6 / 14.6 / 37.4; 67.6 / 24.8 / 48.6 (always HURTS) | Margin gate 62.2 (rate 0.338) / 23.0 (0.124) / 39.6 (0.304); 83.8 / 36.6 / 57.6 | retrieval rate and added seconds per query (+0.01 to +2.2 s) (Tables 1 to 3) | Tables 1 to 3 | The strong-model regime: retrieval hurts on all three single-hop sets |
| Moskvoretskii et al., "Adaptive Retrieval Without Self-Knowledge?", arXiv 2501.12835 | LLaMA-3.1-8B-Instruct | 8B | NQ, SQuAD, TriviaQA, 2Wiki, HotpotQA, MuSiQue; BM25; 500 q each; InAcc (contains) | Never NQ 0.446 / SQuAD 0.176 / TQA 0.636 (LMC 1.0, RC 0) | Always 0.496 / 0.312 / 0.610 (LMC 1.0, RC 1.0) | Max Entropy gate 0.506 (RC 0.73) / 0.312 (1.00) / 0.650 (0.22); Lex-Similarity 0.512 (0.58) / 0.318 / 0.646 (0.22); AdaptiveRAG 0.496 (LMC 2.0, RC 0.98); DRAGIN 0.480 (LMC 4.5, RC 2.24); FLARE 0.450 (3.1, 2.07); SeaKR 0.406 (14.6, 1.00); RowenHybrid 0.494 (55.0, 7.27); Ideal oracle gate 0.608 (1.6, 0.55) / 0.360 / 0.736 (1.4, 0.36) | LMC = LM calls per question including uncertainty calls; RC = retriever calls per question; 35 methods compared; strict EM in Table 7 (NQ 0.386 vs 0.388; TQA 0.592 vs 0.522) | Tables 1, 2, 7 | The cleanest cost convention: report accuracy with (LMC, RC). Our retrieve = (1, 1), agentic = (1 + call rate, call rate) |
| LLM-Independent Adaptive RAG, arXiv 2505.04253 | LLaMA-3.1-8B-Instruct | 8B | NQ etc., same protocol | Never 44.6 | Always 49.6 | Popularity feature 49.8 (RC 0.92); EigValLaplacian 51.2 (0.81); Knowledgability 49.6 (0.95); TriviaQA Popularity 63.2 (RC 0.15) | LMC fixed at 1.0 | Table 1 | Subject popularity alone is a usable but weak gate at 8B |
| ReaLM-Retrieve, arXiv 2604.26649 | R1-Distill-Qwen-32B | 32B | MuSiQue | No retrieval 41.2 EM, 0.0 calls, 12.4 s, 8,432 tokens | Single RAG 52.6, 1.0 calls, 13.2 s | ReaLM 63.5, 1.8 calls, 14.1 s; IRCoT 58.3, 3.4 calls, 18.7 s; Search-R1 59.1, 2.4 calls | retrieval calls, latency, output tokens, dollars per query at $2.19 per 1M tokens: $0.018 to $0.025 (Tables 2, 4, 5) | Tables 2, 4, 5 | Reward penalises calls and latency directly |
| SmartRAG, arXiv 2410.18141 (ICLR 2025) | Flan-T5-large 780M; Llama-2-7B | 0.78B, 7B | PopQA, AmbigNQ, HotpotQA; Bing top-4 | PopQA 7.03; 21.79 EM | Vanilla RAG 34.36; 32.26 | SmartRAG 42.50; 44.32 | retrieval percentage; learns 0 percent when the corpus cannot help (Table 2) | Tables 1, 2 | |
| Self-Routing RAG, arXiv 2504.01018 | Llama-2-7B-Chat; Phi-3.5-mini 3.8B; Qwen2.5-7B | 3.8B to 7B | PopQA, TriviaQA, PubHealth, ARC | | selective-retrieval baseline | +8.5 / +2.1 / +4.7 points with 26 / 40 / 21 percent fewer retrievals | fraction of retrievals saved; 53k training instances | Table 1 | |

---

## 3. Small model plus retrieval beats a much larger model

| Paper | Small model + retrieval | Large model closed-book | Benchmark, metric, setting | Numbers | Citation | Comparable? |
|---|---|---|---|---|---|---|
| RETRO, arXiv 2112.04426 (ICML 2022) | RETRO 7.5B, 2T-token (1,792B) MassiveText chunk database, k up to 10 neighbours | Jurassic-1 178B, Gopher 280B | Pile bits per byte, 16 subsets | RETRO 7.5B beats Jurassic-1 on 10 of 16 and Gopher on 9 of 16 subsets (e.g. github 0.199 vs 0.358 / 0.367; pile_cc 0.626 vs 0.669 / 0.688; loses on dm_mathematics 1.164 vs 1.037 / 1.135); abstract: "comparable performance to GPT-3 and Jurassic-1 on the Pile, despite using 25x fewer parameters" | Table 15, Fig 4 | LM perplexity, not QA |
| same | RETRO 7.5B fine-tuned, DPR top-20 passages | closed-book 7B baseline (fine-tuned) | NQ test EM | 45.5 vs 30.4 (REALM 40.4, DPR 41.5, RAG 44.5, FiD 51.4, FiD+Distill 54.7, EMDR2 52.5); no "retrieval off" NQ row; LM ablation Table 14: Wikitext103 ppl 10.65 baseline / 10.40 Retro[Off] / 2.22 Retro[On] (leakage-inflated) | Table 5, Table 14 | Fine-tuned cross-attention reader; direction and size of the gain (+15) match ours |
| Atlas, arXiv 2208.03299 (JMLR 2023) | Atlas 11B, 64-shot fine-tuned, 40 passages from Wikipedia Dec 2021 (37M passages) plus CCNet (350M total) | PaLM 540B, Chinchilla 70B, Gopher 280B, GPT-3 175B, all 64-shot prompted | NQ EM / TQA-unfiltered EM | Atlas 11B 42.4 / 84.7 vs PaLM 39.6 / 81.4; Chinchilla 35.5 / 72.3; Gopher 28.2 / 61.3; GPT-3 29.9 / 71.2. Full fine-tuning Atlas NQ 60.4 (64.0 with Wikipedia-only index), TQA 89.4 unfiltered / 79.8 filtered | Table 8; abstract: "over 42% accuracy on Natural Questions using only 64 examples, outperforming a 540B parameters model by 3% despite having 50x fewer parameters" | Trained with retrieval; the canonical headline |
| same | Atlas 220M / 770M / 3B / 11B, 64-shot, Dec 2018 Wikipedia index | Chinchilla 70B 35.5 NQ, Gopher 280B 28.2 | NQ 64-shot EM; TQA filtered 64-shot | 27.0 / 35.4 / 41.3 / 45.1 NQ; 55.3 / 65.0 / 70.2 / 71.4 TQA-filtered; full fine-tune NQ 54.1 / 60.8 / 63.4 / 64.0 | Table 19 vs Table 8 | Atlas 3B beats Chinchilla 70B and Gopher 280B on both; Atlas 770M ties Chinchilla on NQ. The cleanest "3B reader plus Wikipedia beats 70B" table; the 64-shot NQ value 41.3 sits inside our oracle band 39 to 68 |
| same | Atlas 11B | GPT-3 175B | MMLU 5-shot | Atlas 47.9 (multi-task 56.6, full 66.0) vs GPT-3 43.9 (full 53.9); "outperforms GPT-3 by 4%, while using 15x less parameters" | Table 7 | |
| REPLUG, arXiv 2301.12652 (NAACL 2024) | frozen GPT-3 with 10 Contriever documents ensembled | | Pile bits per byte | GPT-2 XL 1.5B 1.16 to 1.07 (LSR); Babbage 1.3B 0.95 to 0.88 = Curie 6.7B without retrieval (0.88); Davinci 175B 0.80 to 0.75 (6.3 percent); average LSR gain 7.7 percent | Table 1 | Frozen LM, prepended documents: the same mechanism as ours, but the QA rows are 175B only |
| same | Codex 175B + REPLUG LSR, 16-shot | Codex 175B, Chinchilla 70B 64-shot, PaLM 540B | NQ / TQA-filtered EM | Codex 40.6 / 73.6 to 44.7 / 76.8 (REPLUG) to 45.5 / 77.3 (LSR); Chinchilla 35.5 / 64.6; PaLM 39.6; Atlas 64-shot 42.4 / 74.5 | Table 3 | |
| same | Codex + REPLUG LSR | PaLM 540B, Flan-PaLM 540B | MMLU 5-shot All | 71.8 vs Codex 68.3, PaLM 69.3, Flan-PaLM 72.2, Atlas 11B 47.9 | Table 2 | |
| RA-DIT, arXiv 2310.01352 (ICLR 2024) | RA-DIT 65B (DRAGON+ retriever, 399M chunks Wikipedia 2021 + CommonCrawl, top-10 ensembled) | Llama 65B closed-book | NQ / TQA / MMLU / ELI5, 0-shot and 5-shot | 0-shot: Llama 65B 5.2 / 55.8 / 51.2 / 19.5; REPLUG 65B 28.8 / 72.6 / 59.7 / 19.1; RA-DIT 35.2 / 75.4 / 64.6 / 21.2. 5-shot: 31.6 / 71.8; 42.3 / 74.9; 43.9 / 75.1. 64-shot fine-tune: Atlas 11B NQ 42.4 / TQA 74.5 (8-task avg 56.8) vs RA-DIT 65B 43.5 / 72.8 (avg 60.9) | Table 2, footnote 7 | Strict 0-shot EM at 65B is 5.2 on NQ; retrieval gives +30 |
| In-context RALM, arXiv 2302.00083 (TACL 2023) | GPT-2 345M + BM25 top-1 (Wikipedia 2018, query 32 tokens, stride 4) | GPT-2 762M; GPT-2 1.5B (with trained reranker) | WikiText-103 ppl | GPT-2 S 37.5 to 29.6 (26.8 reranked); M 26.3 to 21.5 (19.7); L 22.0 to 18.1 (16.6); XL 20.0 to 16.6 (15.4): M + BM25 (21.5) beats L (22.0), M + reranker (19.7) beats XL (20.0); OPT 6.7B + RALM matches OPT 66B (Fig 4) | Table 1, Fig 4; intro claims | LM perplexity |
| same | frozen LLaMA-7B / 13B / 33B + top-2 DPR docs, 0-shot | same models closed-book | NQ / TQA EM | 7B 10.3 to 28.0 / 47.5 to 56.0; 13B 12.0 to 31.0 / 54.8 to 60.1; 33B 13.7 to 32.3 / 58.3 to 62.7; "most of the gain can be obtained by using only two documents (or even a single one)" (Fig 8) | Table 4 | Closest published protocol to DAISY-with-lookup: frozen model, 0-shot, one or two prepended passages, strict EM; 7B + 2 docs (28.0) beats 33B closed-book (13.7), the same shape as our 3B + lookup beating 70B closed-book |
| Lazaridou et al., arXiv 2203.05115 | Gopher 1B and 7B + 5 to 20 Google paragraphs, 15-shot prompted | Gopher 280B closed-book | NQ EM | 280B closed 21.7; open-book Google 23.1; gold evidence 61.7; with PoE reranking 38.4; retrieval recall@50 85.0 (Table 1). Scaling (Figs 2, 3): "the open-book 7B model overtakes the closed-book 280B model ... for NQ this is also the case for the even smaller 1B"; "searching the Internet is worth more than 273 billion parameters" (per-size numbers figure only) | Table 1, Figs 2, 3 | The most direct analogue of our claim: 1B plus a few retrieved paragraphs beats 280B closed-book, no training |
| Mallen et al., arXiv 2212.10511 | GPT-Neo 2.7B + Contriever top-1 | GPT-3 davinci-003 vanilla | PopQA acc(contains) | about 0.355 vs 0.34 to 0.35 overall; on the 4,000 least popular questions the 2.7B + Contriever beats davinci-003 | Fig 7, Sec 5.2 | Long-tail entity questions like ours |
| MassiveDS, arXiv 2407.12854 (NeurIPS 2024) | Pythia-1B + 100B-token datastore (Contriever, k = 3); Llama-2 7B + under 100B tokens | Pythia-12B; Llama-2 13B, Llama-3 8B | TriviaQA, NQ | "Pythia-1B matches Pythia-12B when augmented with only 100B tokens ... and outperforms Pythia-12B when further increasing the size of datastore"; Llama-2 7B with retrieval beats Llama-2 13B and Llama-3 8B on TQA and NQ; no gain on MMLU or MedQA | Figs 3, 9, 10 (figure only) | |
| REALM, arXiv 2002.08909 (ICML 2020) | REALM 330M | T5-11B closed-book | NQ / WQ EM | 40.4 / 40.7 vs T5-11B 34.5 / 37.4 (Roberts final: 32.6 / 37.2), "outperforms the largest T5-11B model while being 30 times smaller" | Table 1 | Fine-tuned |
| FiD, arXiv 2007.01282 (EACL 2021) | FiD base 220M / large 770M, DPR 100 passages | T5-11B closed-book 36.6; GPT-3 few-shot 29.9 | NQ / TQA EM | 48.2 / 65.0; 51.4 / 67.6; "the closed book T5 model obtains 36.6% accuracy with 11B parameters, while our approach obtains 44.1% with 770M parameters plus Wikipedia with BM25 retrieval" | Table 1 | Fine-tuned |
| kNN-LM, arXiv 1911.00172 (ICLR 2020) | 247M LM + datastore | same LM trained on 30x more data | WikiText-103 ppl | 18.65 to 16.12 (15.79 with cache); LM trained on WIKI-100M 19.59 to 13.73 with a WIKI-3B datastore, better than an LM trained on all of WIKI-3B (15.17) | Tables 1, 3 | LM only |
| Kandpal et al., arXiv 2211.08411 (ICML 2023) | GPT-Neo + BM25 top-3 or oracle paragraph | BLOOM 176B closed-book | TriviaQA / NQ accuracy vs count of relevant pre-training documents | BLOOM-176B "jumps from 25% to above 55%" from 10^1 to 10^4 relevant docs; 176B has "over 4x higher accuracy than BLOOM-560M" above 10^5 docs; matching the supervised baseline on NQ questions with fewer than 100 relevant docs would need over 10^18 parameters (R^2 0.98 fit); BM25 retrieval "outperform[s] closed-book counterparts across all ranges of relevant document counts" | Figs 1, 6, 7, 9 (figure only) | Danish canon entities are low-document-count entities for every English-heavy model; retrieval, not scale, is the fix |
| Soudani et al., arXiv 2403.01432 | FlanT5-small / base; StableLM2 1.6B; Mistral 7B; Llama2-chat 7B | | PopQA acc, closed-book vs +RAG (retriever detail UNVERIFIED) | 2.69 to 47.46; 6.01 to 73.08; 17.01 to 76.14; 21.47 to 80.25; 26.09 to 81.15 | Table 3 | "Combining FT with RAG yields the best results for smaller models (up to 3B)" |
| 2024 to 2026 paper with a 1 to 4B model + retrieval beating a 70B model closed-book on NQ / TQA / PopQA in a table | | | | none found; nearest are Lazaridou 2022 (1B vs 280B, figure), Mallen 2023 (2.7B vs 175B, figure), Atlas Table 19 vs Table 8 (3B fine-tuned vs 70B / 280B), MassiveDS (1B vs 12B, figure) | | Our DAISY result (3B + lookup 0.28 vs 70B closed 0.225, strict EM, table) is a rare tabulated instance |

---

## 4. Industry search-augmented and tool-use evaluations

### 4.1 SimpleQA (OpenAI, Wei et al. 2024, arXiv 2411.04368): 4,326 English short-fact questions, GPT-4o grader, correct / incorrect / not attempted, F-score = harmonic mean of correct and correct-given-attempted

| Model | Setting | Correct % | Not attempted | Correct given attempted | F-score | Citation | Comparable? |
|---|---|---|---|---|---|---|---|
| Claude-3-haiku / sonnet / opus / 3.5-sonnet | closed-book | 5.1 / 5.7 / 23.5 / 28.9 | 75.3 / 75.0 / 39.6 / 35.0 | 20.6 / 22.9 / 38.8 / 44.5 | 8.2 / 9.2 / 29.3 / 35.0 | arXiv 2411.04368, results table | Same task shape as DAISY closed-book; English, LLM-graded, frontier sizes |
| GPT-4o-mini / GPT-4o / o1-mini / o1-preview | closed-book | 8.6 / 38.2 / 8.1 / 42.7 | 0.9 / 1.0 / 28.5 / 9.2 | 8.7 / 38.0 / 11.3 / 47.0 | 8.6 / 38.4 / 9.4 / 44.8 | same | Calibration: all models overstate confidence; frequency of a sampled answer tracks its accuracy (Sec 4) |
| gpt-4.5-preview / o3 / o1 / o4-mini / o3-mini / gpt-4.1 / 4.1-mini / 4.1-nano / gpt-4o-2024-11-20 | closed-book | 62.5 / 49.4 / 42.6 / 20.2 / 13.4 / 41.6 / 16.8 / 7.6 / 38.8 | | | | github.com/openai/simple-evals README (fetched 4 Sep 2026) | |
| o3 / o4-mini / o1 | closed-book | acc 0.49 / 0.20 / 0.47; hallucination rate 0.51 / 0.79 / 0.44 | | | | o3 and o4-mini system card, Table 4 | |
| gpt-5-thinking / gpt-5-main / thinking-mini / thinking-nano / GPT-4o | closed-book, no web | acc 0.55 / 0.46 / 0.22 / 0.11 / 0.44; hallucination 0.40 / 0.47 / 0.26 / 0.31 / 0.52 | thinking 5 percent, mini 52 percent | | | GPT-5 system card, Table 8 | |
| Gemini 2.5 Pro / 2.5 Flash / 2.0 Flash / 1.5 Pro / 1.5 Flash; o3 / Grok 3 Beta / DeepSeek R1 | closed-book | 54.0 / 26.9 / 29.9 / 24.9 / 8.6; 48.6 / 43.6 / 27.8 | | | | arXiv 2507.06261v2 (Gemini 2.5 report), Table 4 | |
| DeepSeek-V3 / R1; Llama-3.1-405B-Inst; Qwen2.5-72B-Inst | closed-book | 24.9 / 30.1; 17.1; 9.1 | | | | DeepSeek-V3 and R1 model cards | |
| Kimi K2 Instruct; Claude Sonnet 4 / Opus 4; Qwen3-235B-A22B non-thinking; Qwen3-235B-Instruct-2507 | closed-book | 31.0; 15.9 / 22.8; 13.2; 54.3 | | | | Kimi K2 card; Qwen3-235B-A22B-Instruct-2507 card | |
| Gemma 3 1B / 4B / 12B / 27B IT; Gemma 2 27B | closed-book | 2.2 / 4.0 / 6.3 / 10.0; 9.2 | | | | arXiv 2503.19786, Table 6 | Our size class: 4B scores 4.0 on English SimpleQA, 5.6 on Danish DAISY |
| phi-4 14B; phi-3 14B; Qwen2.5-14B; GPT-4o-mini; Llama-3.3-70B; Qwen2.5-72B; GPT-4o | closed-book | 3.0; 7.6; 5.4; 9.9; 20.9; 10.2; 39.4 | | | | arXiv 2412.08905, Table 1 | Llama 3.3 70B: 20.9 SimpleQA vs 22.5 DAISY |
| Llama 3.2 3B, Qwen 2.5 3B, Qwen3 4B, Phi-4-mini | closed-book | no vendor SimpleQA number | | | | checked cards and reports | UNVERIFIED / not published |
| SimpleQA Verified (Google DeepMind, 1,000 prompts, gpt-4.1 grader): Gemini 2.5 Pro / GPT-5 / o3 / GPT-4.1 / GPT-4o / DeepSeek R1 / Claude Opus 4 / Gemini 2.5 Flash / GPT-5 Mini / o4-mini / Claude Sonnet 4 / GPT-5 Nano | closed-book | F1 55.6 / 52.3 / 51.9 / 39.9 / 34.9 / 33.3 / 28.3 / 28.2 / 24.6 / 23.4 / 18.7 / 14.4; attempted 98.9 / 94.6 / 99.3 / 99.3 / 97.0 / 96.4 / 35.5 / 96.9 / 40.4 / 96.5 / 33.9 / 42.2 | | | | arXiv 2509.07968, Table 7; Gemini 3 Pro 72.1 (blog.google, 18 Nov 2025) | Claude abstains on two thirds; the "not attempted" column is the abstention behaviour we probe with the yes/no scaffold |
| FACTS Parametric (Google, 2,104 Wikipedia-verified questions, closed-book) | closed-book | Gemini 3 Pro 76.4; Gemini 2.5 Pro 63.2; Grok 4 58.5; o3 57.0; GPT-5 55.7; GPT-4.1 51.5; Claude 4.1 Opus 33.2; Claude 4.5 Opus 30.5; Claude 4.5 Sonnet 28.9; Gemini 2.5 Flash 30.6; Claude 4 Sonnet 20.3; o4 mini 20.4; GPT-5 mini 16.0 | | | | FACTS benchmark suite paper (Google), Table 6 | |

### 4.2 Published "with search versus without" pairs

| System | Without search | With search | Metric | Citation | Comparable? |
|---|---|---|---|---|---|
| gpt-4o vs gpt-4o-search-preview | 38.2 to 40.1 | 90 | SimpleQA correct % | openai.com/index/new-tools-for-building-agents (11 Mar 2025) and simple-evals | Full web search plus snippets, frontier model |
| gpt-4o-mini vs gpt-4o-mini-search-preview | 8.6 to 9.5 | 88 | SimpleQA | same | The industry version of our jump: a weak closed-book model reaches near-ceiling with search |
| Perplexity Sonar Pro / Sonar; Perplexity Deep Research | | F-score 0.858 / 0.773; 93.9 percent | SimpleQA | perplexity.ai blog, Jan and Feb 2025 | vendor |
| Tavily search + GPT-4.1 reader ("no prior knowledge allowed") | GPT-4.1-mini 41.6 | 93.3 | SimpleQA | tavily.com blog, 18 Jun 2025 | Closest in spirit to answer-from-retrieved-text-only; vendor |
| Linkup Deep Search / Exa / Sonar Pro / Sonar / Tavily / Grok 3 | | 90.1 (later 91.0) / 90.04 / 86 / 77 / 73 / 45 | SimpleQA | linkup.so blog (vendor compilation) | UNVERIFIED beyond the vendor page |
| Firecrawl search + GPT-5.4 agent | GPT-5.4 43.8 | 94.7 | SimpleQA | firecrawl.dev blog, 22 Jul 2026 | vendor |
| Qwen3-4B with MCP Google search + scrape; Jan-nano 4B (fine-tuned Qwen3-4B); Jan-nano-128k; DeepSeek-671B with MCP | | 59.2; 80.7; 83.2; 78.2 | SimpleQA | arXiv 2506.22760 (Jan-nano), Table 1 | The only 4B "with search" number on SimpleQA; Google plus full-page scrape, multiple calls; the paper warns MCP implementations differ |
| FACTS Search (1,884 questions needing search): Gemini 3 Pro / GPT-5 / Grok 4 / o3 / Claude 4.5 Opus / 4.5 Sonnet / GPT-5 mini / o4 mini / Claude 4.1 Opus / Claude 4 Sonnet / GPT-4.1 / Gemini 2.5 Pro / 2.5 Flash / GPT-5.1 | FACTS Parametric 76.4 / 55.7 / 58.5 / 57.0 / 30.5 / 28.9 / 16.0 / 20.4 / 33.2 / 20.3 / 51.5 / 63.2 / 30.6 / 43.2 | 83.8 (3.39 searches avg) / 77.7 (4.28) / 75.3 / 74.8 / 73.2 / 69.8 / 67.9 / 66.2 / 65.0 / 66.3 / 64.6 / 63.9 / 60.0 / 62.4 | accuracy | FACTS paper Tables 6 and 8 | Different question sets; the only vendor table that prints searches per question |
| GPT-5 with browsing vs o3 / GPT-4o | | gpt-5-main 26 percent fewer hallucinated claims than GPT-4o; gpt-5-thinking 65 percent fewer than o3; "over 5 times fewer factual errors than o3 in both browsing settings" | claim-level hallucination rate | GPT-5 system card Sec 3.7 | Rates, not QA accuracy |
| Gemini Grounding with Google Search; Anthropic web search tool | | no accuracy pair published | | ai.google.dev grounding docs checked; anthropic.com | none |

### 4.3 BrowseComp (OpenAI, arXiv 2504.12516; 1,266 hard multi-hop questions, LLM-judged) and FRAMES (Google, arXiv 2409.12941; 824 multi-hop questions over 2 to 15 Wikipedia articles, LLM autorater)

| Benchmark | Model | Size | Setting | Number | Citation | Comparable? |
|---|---|---|---|---|---|---|
| BrowseComp | GPT-4o / GPT-4o with browsing / GPT-4.5 / o1 / Deep Research | closed | | 0.6 / 1.9 / 0.9 / 9.9 / 51.5 (calibration error 69 / 82 / 68 / 65 / 91); humans 29.2 percent within 2 hours | arXiv 2504.12516, Tables 2, 3 | Needs 10 to 25 searches per question; not our task shape |
| BrowseComp | o3 with search / GPT-5 high / GPT-5.2 Thinking / GPT-5.2 Pro / Gemini 3 Pro / Gemini 3.1 Pro / Claude Opus 4.6 / Claude Opus 4.5 / Claude Sonnet 4.5 / Kimi K2 Thinking / Tongyi DeepResearch 30B-A3B / MiroThinker 8B / 30B / 72B / DeepSeek-V3.2 | | agentic with tools | 49.7 / 54.9 / 65.8 / 77.9 / 59.2 / 85.9 / 84.0 (86.8 multi-agent) / 67.8 / 19.6 to 43.9 by harness / 60.2 / 43.4 / 31.1 / 41.2 / 47.1 / 40.1 | Tongyi DeepResearch Table 1 (arXiv 2510.24701); Kimi K2 Thinking card; MiroThinker Table 1 (arXiv 2511.11793); deepmind.google pro page; anthropic.com Opus 4.6 post; vellum.ai (secondary) for Opus 4.5 and the 43.9 | Harness-dependent; o4-mini 28.3, GPT-5 Pro, Claude 4 / 4.1, Gemini 2.5 Deep Research, Grok 4 Heavy, Kimi-Researcher UNVERIFIED or unpublished |
| BrowseComp-en | WebSailor 3B / 7B / 32B / 72B; WebDancer-QwQ 32B; WebThinker-RL 32B | | agentic | 3.3 / 6.7 / 10.5 / 12.0; 3.8; 2.8 | arXiv 2507.02592, Table 1 | A trained 3B browsing agent scores 3.3 |
| BrowseComp-Plus (830 q, fixed 100,195-document corpus, ReAct agent) | gpt-5 / o3 / gpt-oss-120B / gpt-4.1 / Claude Sonnet 4 / Opus 4 / Gemini 2.5 Pro / 2.5 Flash / Qwen3-32B / Search-R1-32B | | BM25 accuracy (avg search calls); Qwen3-Embedding-8B accuracy (calls) | 55.90 (23.23), 70.12 (21.74) / 49.28 (25.93), 63.49 (23.97) / 28.67 (19.45), 42.89 (18.35) / 14.58 (10.35), 35.42 (8.67) / 14.34 (9.95), 36.75 (9.03) / 15.54 (11.22), 36.14 (10.24) / 19.04 (7.44), 28.67 (6.04) / 15.54 (10.56), 33.01 (9.77) / 3.49 (0.92), 10.36 (0.94) / 3.86 (1.78), 10.36 (1.69); oracle gold docs gpt-4.1 93.49 | arXiv 2508.06600, Table 1, Sec 4.8.1 | Prints search calls per question; a 32B model with under one call per question is at 3 to 10 percent |
| FRAMES | Gemini 1.5 Pro / 1.5 Flash / Gemma2-27b / Llama3.2-3B / Qwen2.5-3B | | naive prompt, no retrieval | 0.408 / 0.263 / 0.308 / 0.115 / 0.095 | arXiv 2409.12941, Table 3 | The only FRAMES rows in our size class |
| FRAMES | Gemini 1.5 Pro / 1.5 Flash | | BM25 n_doc 2 / 4; oracle gold articles; multi-step (up to 5 steps, 10 docs) | 0.452 / 0.474; 0.288 / 0.315; oracle 0.729 / 0.665; multi-step 0.66 (Pro) | same, Table 3 and abstract | Oracle-prompt row = our retrieve-oracle idea at frontier scale |
| FRAMES | Tongyi DeepResearch / o3 / DeepSeek-V3.1 / GLM-4.5 / Kimi K2 / Kimi Researcher / Claude-4-Sonnet; Kimi K2 Thinking / GPT-5 high / Claude Sonnet 4.5; MiroThinker 8B / 30B / 72B | | agentic | 90.6 / 84.0 / 83.7 / 78.9 / 72.0 / 78.8 / 80.7; 87.0 / 86.0 / 85.0; 80.6 / 85.4 / 87.1 | Tongyi Table 1; Kimi K2 Thinking card; MiroThinker Table 1 | |

### 4.4 Tool calling: BFCL V4 (gorilla.cs.berkeley.edu/leaderboard.html, "Last Updated 2026-04-12", data_overall.csv fetched 4 Sep 2026) and tau-bench

| Model | Overall | Non-live AST | Live | Multi-turn | Web search | Citation | Comparable? |
|---|---|---|---|---|---|---|---|
| Claude-Opus-4-5 (FC) / Claude-Sonnet-4-5 (FC) / Gemini-3-Pro-Preview (Prompt) | 77.47 / 73.24 / 72.51 | 88.58 / 88.65 / 90.65 | 79.79 / 81.13 / 83.12 | 68.38 / 61.37 / 60.75 | 84.50 / 81.00 / 80.00 | BFCL V4 leaderboard | The "Web search" column is the closest published proxy for our agentic condition (issue a search call, read, answer) |
| o3 / Kimi-K2-Instruct / GPT-5.2 (FC) / GPT-4.1 (FC) | 63.05 / 59.06 / 55.87 / 53.96 | 81.94 / 81.60 / 81.85 / 82.79 | 73.21 / 78.68 / 70.39 / 69.95 | 62.25 / 50.63 / 28.12 / 38.88 | 50.50 / 66.50 / 75.50 / 68.00 | same | |
| xLAM-2-8b-fc-r / Qwen3-8B / ToolACE-2-8B / xLAM-2-3b-fc-r / Qwen3-4B-Instruct-2507 / Hammer2.1-7b / xLAM-2-1b-fc-r / Gemma-3-12b-it / Hammer2.1-3b / Gemma-3-27b-it / Phi-4 / Llama-3.1-8B-Instruct | 46.68 / 42.57 / 42.44 / 41.22 / 35.68 / 31.67 / 30.44 / 30.43 / 29.71 / 29.47 / 28.79 / 25.83 | 84.58 / 87.58 / 87.10 / 82.96 / 87.88 / 85.50 / 69.04 / 79.44 / 84.96 / 87.17 / 69.56 / 84.00 | 67.95 / 80.53 / 77.42 / 62.92 / 76.39 / 69.50 / 55.14 / 74.24 / 70.54 / 74.54 / 60.70 / 70.76 | 70.00 / 41.75 / 38.38 / 58.38 / 22.12 / 23.87 / 36.00 / 5.75 / 16.50 / 10.75 / 3.88 / 11.12 | 6.50 / 12.00 / 8.50 / 2.50 / 3.00 / 0.00 / 0.00 / 4.00 / 0.00 / 0.00 / 4.50 / 3.00 | same | Small open models do simple function calls well (non-live AST 80 to 88) and open-ended web search badly (0 to 12) |
| Llama-3.2-3B-Instruct (FC) / Gemma-3-4b-it (Prompt) / Llama-3.2-1B-Instruct (FC) / Gemma-3-1b-it (Prompt) | 21.95 / 19.62 / 10.82 / 7.17 | 82.67 / 61.12 / 38.38 / 20.21 | 58.33 / 60.84 / 11.77 / 11.84 | 4.00 / 0.38 / 0.00 / 0.00 | 1.00 / 1.00 / 0.00 / 0.00 | same | Our models: 1 percent on BFCL web search versus 40 percent EM on our fixed single-query Wikipedia tool; our task is far simpler than an open tool loop |
| Qwen2.5-3B / 7B-Instruct, Phi-4-mini, watt-tool, GPT-4o on V4 | | | | | | absent from the current CSV | UNVERIFIED |
| Older BFCL versions: Phi-4-mini 70.3, Llama-3.2-3B 78.6, Qwen2.5-3B 74.2, Qwen2.5-7B 81.3, Llama-3.1-8B 77.0 (version unstated); BFCL-v3: Qwen3-4B-Instruct-2507 61.9, Qwen3-235B-Instruct-2507 70.9, GPT-4o-0327 66.5, Kimi K2 65.2 | | | | | | arXiv 2503.01743 Table 7; Qwen model cards | Not comparable across versions |
| tau-bench retail / airline pass^1: gpt-4o 61.2 / 35.2; claude-3-opus 44.2 / 34.7; llama-3-70B 14.8 / 14.4 (paper); claude-3-5-sonnet-20241022 0.692 / 0.460 (README); Claude Opus 4 81.4 / 59.6, Sonnet 4 80.5 / 60.0, o3 70.4 / 52.0, GPT-4.1 68.0 / 49.4 (Anthropic Claude 4 post); GPT-4.1-mini 55.8 / 36.0, 4.1-nano 22.6 / 14.0 (OpenAI GPT-4.1 post); Qwen3-4B-Instruct-2507 TAU1 48.7 / 32.0, TAU2 40.4 / 24.0 (card) | | | | | | arXiv 2406.12045 Table 2; github sierra-research/tau-bench; vendor posts; Qwen card | Multi-turn agentic; the only small open model number is Qwen3-4B |
| tau2-bench retail / airline / telecom: GPT-4.1 74 / 56 / 34; later Gemini 3.1 Pro 90.8 retail / 99.3 telecom; Claude Opus 4.6 91.9 / 99.3; GPT-5.2 82.0 / 98.7 | | | | | | arXiv 2506.07982 (Fig 3, approximate); deepmind.google pro page | |

---

## 5. Calibration, self-knowledge and selective QA

### 5.1 Kadavath et al. 2022, "Language Models (Mostly) Know What They Know", arXiv 2207.05221 (models 800M, 3B, 12B, 52B; no smaller)

| Result | Model | Task | Method | Metric | Number | Where | Comparable? |
|---|---|---|---|---|---|---|---|
| Calibration improves with size and with shots | 800M to 52B | BIG Bench MC, 5-shot | option probabilities | ECE | lettered choices about 0.14 (800M) to 0.02 (52B); True/False 0.10 to 0.01 (read from figure) | Fig 4 right, Sec 2 | Multiple choice with visible options; our task is open generation |
| P(True) self-evaluation | 3B / 12B / 52B | TriviaQA | one example, prompt | AUROC | 0.63 / 0.82 / 0.81 (read from figure) | Fig 31 (App C) | Closest analogue to our yes/no probe; note 20-shot |
| same with 5 comparison samples | 3B / 12B / 52B | TriviaQA | comparison samples, prompt / 20-shot | AUROC | 0.77 / 0.85 / 0.885; 20-shot 0.55 / 0.82 / 0.885 | Fig 31 | The 3B model collapses to near chance at 20-shot |
| P(True) other tasks | 3B / 12B / 52B | Lambada; Arithmetic; Codex; GSM8K | one example / comparison / 20-shot | AUROC | Lambada 0.54, 0.76, 0.73 / 0.81, 0.85, 0.90 / 0.52, 0.84, 0.88; Arithmetic 0.38, 0.62, 0.75 / 0.65, 0.69, 0.94 / 0.70, 0.75, 0.92; Codex 0.58, 0.70, 0.83 / 0.52, 0.73, 0.82 / 0.50, 0.55, 0.65; GSM8K 0.52, 0.63, 0.72 / 0.54, 0.54, 0.69 / 0.42, 0.45, 0.55 | Fig 31 | |
| Zero-shot P(True) | all | all | 0-shot | calibration | "poorly calibrated, typically close to 50%" | Sec 4.1, Fig 38 | Our yes/no probe is zero-shot: this is the expected regime |
| Small models trivially calibrated | 800M, 3B | GSM8K, Codex, Arithmetic | P(True) | | "smaller models get almost every question wrong ... only well-calibrated because they are making trivial predictions" | Figs 30, 32 captions | Llama 1B saying no to everything is this failure mode |
| P(IK) in-distribution | 52B | TriviaQA held-out | trained value head | AUROC / Brier | 0.864 / 0.151 (TriviaQA only); 0.873 / 0.145 (all tasks) | Table 1 | Needs a trained head |
| P(IK) out of distribution | 52B | Mixed-Arith / Lambada / Py Func / GSM8K | trained on TriviaQA vs on all | AUROC | 0.928 vs 0.987; 0.606 vs 0.853; 0.687 vs 0.881; 0.624 vs 0.752 | Table 1 | |
| P(IK) AUROC by size | 800M / 3B / 12B / 52B | TriviaQA in-dist.; Mixed-Arithmetic OOD | trained head | AUROC | 0.81 / 0.88 / 0.875 / 0.865; OOD 0.37 / 0.61 / 0.77 / 0.93 (read from figure) | Fig 14 | In-distribution P(IK) is strong at 800M; size shows in OOD transfer |
| Source material raises P(IK) | 52B | TriviaQA with the Wikipedia article prepended | P(IK) without retraining | P(IK) | example 18 percent to 78 percent; average gain about 0.14 to 0.28 (read from figure) | Sec 5.3, Fig 18 | Analogue of our retrieve-oracle condition, at 52B |

### 5.2 Follow-ups: AUROC of correctness prediction, smallest models first

| Paper | Model, size | Task | Method | Metric | Number | Citation | Comparable? |
|---|---|---|---|---|---|---|---|
| ASPIRE, arXiv 2310.11689 | GPT2-XL 1.5B pre-trained | TriviaQA | Perplexity / Predictive Entropy / Semantic Entropy / Self-eval / P(True) | AUROC (AUACC) | 72.88 (22.60) / 76.20 (24.83) / 75.33 (24.37) / 42.75 (9.30) / 44.54 (10.62) | Table 1 | 1.5B: token entropy 0.76, prompted self-evaluation below chance |
| same | OPT-2.7B pre-trained (TriviaQA acc 21.38) | TriviaQA | same | AUROC (AUACC) | 78.86 (40.93) / 78.92 (41.20) / 78.06 (40.72) / 59.04 (25.88) / 56.89 (24.88) | Table 1 | Closed-book accuracy 21 percent is near our regime |
| same | OPT-30B pre-trained (acc 39.36) | TriviaQA | Self-eval / P(True) | AUROC | 48.90 / 45.63 | Table 1 | Prompted self-eval stays at chance at 30B for base models |
| same | OPT-2.7B soft-prompt tuned | TriviaQA | SE / ASPIRE learned self-eval | AUROC | 81.55 / 84.44 | Table 1 | |
| Kuhn et al. (Semantic Uncertainty), arXiv 2302.09664 (ICLR 2023) | OPT 2.7B / 6.7B / 13B / 30B | TriviaQA (Rouge-L > 0.3 correctness), 10 samples | SE; normalised entropy; predictive entropy; lexical similarity; p(True) | AUROC | SE 0.77 / 0.81 / 0.82 / 0.83; norm. ent. 0.75 / 0.78 / 0.79 / 0.80; pred. ent. 0.77 / 0.79 / 0.80 / 0.79; lexical 0.72 / 0.73 / 0.75 / 0.77; p(True) 0.59 / 0.66 / 0.65 / 0.69 (read from figure) | Fig 2b; Table 2 (30B: SE 0.83, distinct answers 0.79) | At 2.7B plain predictive entropy gives 0.77 on short answers; p(True) is weakest at every size |
| Farquhar et al., Nature 630 (2024) | LLaMA 2 Chat 7B / 13B / 70B, Falcon Instruct 7B / 40B, Mistral 7B | TriviaQA, SQuAD, BioASQ, NQ-Open, SVAMP (400 q each), 10 samples | semantic entropy / naive entropy / P(True) / embedding regression | AUROC averaged over 30 model x dataset pairs | 0.790 / 0.691 / 0.698 / 0.687; SE per-model 0.78 to 0.81 | Results text, Fig 2; per-pair values in Supplementary (UNVERIFIED, not fetched) | Model-agnostic; needs sampling plus an NLI model |
| INSIDE, arXiv 2402.03744 (ICLR 2024) | LLaMA-7B; OPT-6.7B; LLaMA-13B | TriviaQA 9,960; NQ-Open 3,610 | Perplexity / LN-Entropy / Lexical Sim / EigenScore | AUROC (sentence-sim correctness) | LLaMA-7B TriviaQA 83.6 / 83.4 / 82.6 / 82.7; NQ 74.0 / 72.8 / 73.8 / 76.5; OPT-6.7B TriviaQA 82.6 / 79.8 / 78.2 / 80.3; LLaMA-13B TriviaQA perplexity 84.7 | Table 1 | On short answers plain perplexity of a 7B model already gives 0.84; NQ is harder (0.75) |
| Orgad et al., arXiv 2410.02707 (ICLR 2025) | Mistral-7B-Instruct; Llama 3 8B Instruct | TriviaQA | logits-mean / logits-min-exact / p(True) / probe on exact-answer token | AUC | Mistral 0.60 / 0.75 / 0.66 / 0.85; Llama 3 8B 0.66 / 0.79 / 0.73 / 0.83 | Table 1 | Minimum logit over the exact answer tokens gives 0.75 to 0.79 with no training |
| Ulmer et al. (APRICOT), arXiv 2403.05973 | Vicuna v1.5 7B (TriviaQA acc 58 percent) | TriviaQA; CoQA | sequence likelihood / Platt / verbalised qualitative / verbalised percent / auxiliary calibrator | AUROC (Brier, ECE) | TriviaQA .79 (.22, .05) / .70 / .62 (parsed in only 19 percent of outputs) / .52 (.39, .38) / .83; CoQA .69 / .69 / .48 / .53 / .82 | Table 3 | Verbalised percent confidence from a 7B model is at chance (0.52) |
| Xiong et al., arXiv 2306.13063 (ICLR 2024) | Vicuna 13B; LLaMA 2 70B; GPT-3; GPT-3.5; GPT-4 | 8 reasoning tasks | vanilla verbalised confidence | ECE / AUROC (x100, avg) | 46.1 / 52.5; 43.6 / 56.4; 52.0 / 51.3; 37.7 / 55.1; 18.0 / 62.7 | Table 2 | Verbalised confidence "predominantly fall[s] within the 80% to 100% range" (Sec 5.1): our Llama 3B claiming to know 88 percent of what it gets wrong |
| same | GPT-3.5 | GSM8K | self-consistency, 5 samples | AUROC | 54.8 (single) to 92.7 | Table 3 | Sampling agreement is the cheap fix; feasible on a 1060 for 1 to 3B |
| Yin et al. (SelfAware), arXiv 2305.18153 | GPT-3 ada 350M / babbage 1.3B / curie 6.7B / davinci 175B; InstructGPT same sizes; LLaMA 7B / 13B / 65B; Vicuna 7B / 13B; GPT-4; human | 1,032 unanswerable + 2,337 answerable | direct / instruction / ICL hedging detection | F1 (unanswerable positive) | base ICL 34.27 / 36.27 / 47.24 / 55.5; InstructGPT ICL 47.93 / 48.42 / 55.81 / 65.12; LLaMA instruction 28.57 / 30.12 / 46.89; Vicuna 42.78 / 47.84; GPT-4 75.47; human 84.93 | Figs 2, 3, 5 | Measures hedging on unanswerable questions; below 7B base models barely move, instruction tuning matters more than size |
| Wagner 2026, arXiv 2607.08456 | Gemma 2 2B / Qwen2.5 3B / Qwen2.5 7B / Llama 3.1 8B / Qwen2.5 14B | SelfAware 150 + 150 (closed-book acc 0.28 / 0.30 / 0.35 / 0.42 / 0.37) | trained output-confidence readout; prompt-token hidden-state probe; verbalised P(IK) / P(True) on CREPE | AUROC correctness | readout 0.82 / 0.80 / 0.77 / 0.84 / 0.64; hidden probe 0.64 / 0.59 / 0.80 / 0.88 / 0.86; verbalised P(IK) 0.66 / 0.59 / 0.60 / 0.63 / 0.54, P(True) 0.54 / 0.58 / 0.55 / 0.54 / 0.55 | Tables 1, 2 | Closest to our size class: Qwen2.5 3B output confidence separates right from wrong at 0.80; verbalised self-knowledge near chance |
| Influences on LLM Calibration, arXiv 2501.03991 | Gemma2-2b; Llama2-7b | TriviaQA (2,000 train / 1,000 test) | auxiliary calibrator Calib-1 / Calib-n | AUC (ECE, Brier) | Gemma2-2b 0.645 (0.084, 0.238) / 0.685 (0.128, 0.240); Llama2-7b 0.683 / 0.705 | Table 2 | The only 2B TriviaQA AUROC found |
| Revisiting UE and Calibration, arXiv 2505.23854 | Llama 3.2 1B (of 80 models 0.6B to 671B) | MMLU-Pro | numerical verbal / token probability | ECE / AUROC | NVU 0.510 / 0.525; TPU 0.573 / 0.463 | Tables 3, 4 (as fetched) | Llama 3.2 1B at chance; "Qwen3-0.6B and 1.7B achieve only random-level performance" |
| Semantic Self-Distillation, arXiv 2602.04577 | Llama 3.2 3B, SmolLM3 3B, Qwen3 4B, Gemma 3 4B, Llama 3.1 8B, Qwen3 8B, Ministral 8B | TriviaQA 1,000 | SE / correctness probe / SE probe / SSD | AUROC macro over models | 0.804 / 0.771 / 0.759 / 0.708; Llama 3.2 3B SSD 73.7 | Table 2, Table A5 | Only paper with Llama 3.2 3B and Gemma 3 4B on TriviaQA; per-model SE values UNVERIFIED |
| Zero-Shot Confidence for Small LLMs, arXiv 2605.02241 | Qwen 2.5 7B / Llama 3.1 8B / Mistral 7B | MMLU-Pro; TriviaQA 500 | mean token log-prob vs supervised router | AUROC | logprob 0.714 / 0.650 / 0.678 (MMLU-Pro); TriviaQA transfer logprob 0.782 vs supervised 0.546 | Tables III, IV | Use token probability first |
| Kapoor et al., arXiv 2406.08391 (NeurIPS 2024) | LLaMA 2 7B / 13B, Mistral 7B and chat variants | MMLU MC and open-ended | LoRA-tuned uncertainty head | ECE / AUROC (mean of six) | 10.8 / 71.6 (with KL); zero-shot and verbalised "perform poorly" (figure only) | Table 1, Fig 3 | About 1,000 labelled examples suffice |
| LM-Polygraph benchmark, arXiv 2406.15627 (TACL 2025) | Mistral 7B v0.2 base | TriviaQA (AlignScore quality) | MSP / Perplexity / Mean Token Entropy / SAR / DegMat / P(True) | PRR (0 = random, 1 = oracle) | 0.63 / 0.64 / 0.64 / 0.67 / 0.67 / minus 0.12 | Table 7 | Short outputs (1 to 2 symbols) favour MSP and perplexity (PRR 0.71, Table 4); P(True) below random, "LLMs being too small to develop an awareness of their own knowledge gaps" (Sec 6.1) |
| R-Tuning, arXiv 2311.09677 | OpenLLaMA-3B / LLaMA-7B / 13B | ParaRel, MMLU, 5-task average, HaluEval-QA | refusal tuning vs vanilla, AP ranked by confidence | AP (percent) | 5-task avg 61.09 vs 58.24; 69.11 vs 68.94; 76.03 vs 71.71; ParaRel OOD 69.41 vs 68.42; 74.61 vs 78.08; 77.30 vs 64.12 | Tables 1, 13 | Gains from refusal tuning are small or negative at 3B and grow with size |
| Knowledge-Weighted FT, arXiv 2604.05779 | Llama 3.2 3B | HaluEval / MedQA / SciQ | IDK fine-tuning | IDK precision; abstain false-positive rate | 92.1 / 91.2 / 78.3; 11.4 / 21.6 / 3.7 | Tables 5, 6 | A 3B model learns high-precision abstention after fine-tuning |
| Kang et al., arXiv 2403.05612 | Llama 2 7B | TriviaQA, MMLU, biographies | unfamiliar fine-tuning examples | qualitative | predictions on unfamiliar queries "default towards the distribution of target responses in the model's unfamiliar finetuning examples"; labelling unfamiliar examples "I don't know" yields abstention on unfamiliar test queries | Figs 2, 3 (numbers figure-only, UNVERIFIED) | Why an instruction-tuned 1B may say no to everything |
| Moskvoretskii et al., arXiv 2501.12835 | LLaMA 3.1 8B Instruct | NQ / TriviaQA / SQuAD self-knowledge | Max Entropy / Mean Entropy / SAR / Lex-Sim / EigVal / SeaKR / AdaptiveRAG classifier | ROC-AUC | 0.62 / 0.62 / 0.63 / 0.63 / 0.60 / 0.64 / 0.54; 0.71 / 0.72 / 0.73 / 0.74 / 0.71 / 0.78 / 0.49; 0.69 / 0.74 / 0.71 / 0.67 / 0.57 / 0.77 / 0.58 | Table 2 | Single-pass entropy gives 0.62 to 0.74 as a retrieval trigger at 8B |
| Can SLMs use what they retrieve, arXiv 2603.11513 | SmolLM2 360M / Qwen2.5 1.5B / 3B / 7B (NF4) / Llama 3.1 8B | NQ 500 + HotpotQA 500 | oracle passage on questions the model could not answer closed-book | accuracy | 0.0 / 10.0 / 12.8 / 14.6 percent; on known questions oracle context drops accuracy to 43.0 / 54.4 / 58.4 | Table 4 | Opposite sign to our retrieve-oracle (39 to 68); their corpus is 2 percent of Wikipedia and their prompt format is untested against ours |

### 5.3 Selective QA and abstention

| Paper | Model, size | Task | Method | Metric | Number | Citation | Comparable? |
|---|---|---|---|---|---|---|---|
| Kamath, Jia, Liang, arXiv 2006.09462 (ACL 2020) | BERT-base QA on SQuAD 1.1 | 50 percent SQuAD + 50 percent unknown OOD (MRQA) | MaxProb / calibrator (SQuAD only) / calibrator (SQuAD + known OOD) / best possible | AUC of risk-coverage (lower better) / Cov@Acc80 / Cov@Acc90 | 20.54 / 48.23 / 21.07; 19.27 / 53.67 / 26.68; 18.47 / 56.06 / 29.42; 9.64 / 74.92 / 66.59 | Table 1 | Definitions (Sec 3): coverage = fraction answered; risk = error on answered; AUC integrates risk over coverage; Cov@Acc = max coverage with accuracy at least the target. Calibrator = random forest on softmax, lengths and similar features |
| same | same | same | test-time dropout features (K = 30) | AUC / Cov@80 | calibrator both + dropout 17.31 / 59.99 | Table 2 | |
| Wen et al. survey, arXiv 2407.18418 (TACL 2025) | none | metric definitions | | | abstention precision N5/(N3+N5); abstention recall N5/(N2+N4+N5); coverage (N1+N2+N4)/N; reliable accuracy N1/(N1+N2+N4); effective reliability (N1 minus N2 minus N4)/N; Coverage@Acc; AURCC (lower better); AUACC (higher better) | statistical evaluation section, Table 1 | Use these names on the page |
| AbstentionBench, arXiv 2506.09038 | Llama 3.1 8B Inst / Mistral 7B v0.3 / OLMo 7B / Llama 3.1 8B Base / Llama 3.1 70B Inst / 405B Inst / GPT-4o / Qwen2.5 32B / o1 / DeepSeek R1 Distill 70B | 20 datasets, over 35k unanswerable questions | | abstention recall (avg accuracy) | 0.66 (0.70) / 0.63 (0.69) / 0.54 (0.56) / 0.44 (0.42) / 0.64 (0.74) / 0.68 (0.74) / 0.69 (0.75) / 0.71 (0.75) / 0.66 (0.80) / 0.46 (0.81) | Table 4 | "model scale has almost no effect on abstention performance"; reasoning fine-tuning lowers abstention 24 percent on average; no 1 to 4B models |
| Yadkori et al., arXiv 2405.01563 | Gemini Pro | TriviaQA 1,000; Temporal Sequences 4,000 | conformal risk control on match-count self-consistency vs log-prob | abstention rate at hallucination risk 0.1 | TriviaQA about 10 to 11 percent (match count) vs 11 to 15 percent (log-prob); Temporal 11.7 vs 22.8 | Tables 1, 7, 8 | Distribution-free risk bound; transfers to any scorer given a Danish calibration set |
| GRAB-RAG, arXiv 2608.22228 | Phi-4-mini 3.8B / Llama 3.1 8B / Qwen2.5 7B | NQ 500, HotpotQA 500, RAG with missing or misleading context | prompt-based abstention | answered-when-should-abstain rate | evidence missing at or below 3 percent; misleading context 41.6 percent macro (Phi-NQ 43.1, Llama-NQ 74.3, Qwen-NQ 71.3) | Tables 1, 2 | A wrong Wikipedia page will be trusted by 4 to 8B models |
| Madhusudhan et al., arXiv 2407.16221 | Mistral 7B, Mixtral, GPT-3.5, GPT-4 | Abstain-QA 2,900 MCQ | abstain clause / verbal confidence / CoT | abstention rate, accuracies | per-model numbers UNVERIFIED | Table 1 | |
| Head-to-Tail, arXiv 2308.10168 (NAACL 2024) | GPT-4 / ChatGPT / Llama 2 70B / LLaMA 33B | 18,171 QA pairs; head / torso / tail by entity traffic thirds | accuracy A, hallucination H, missing M (ChatGPT-judged) | overall A, H | 30.9, 19.7 / 20.3, 14.1 / 11.8, 34.0 / 18.2, 80.0 | Table 3 | Popularity terciles are a ready-made trigger for our subjects |
| same | GPT-4; Llama 2 70B | head / torso / tail | A; H | 40.3 / 33.4 / 19.0; 23.3 / 19.7 / 15.9. 16.2 / 13.2 / 6.1; 30.3 / 33.0 / 38.6 | Table 4 | |
| same | LLaMA 7B; Vicuna 7B; Vicuna 13B; Falcon 7B; Flan-T5 3B; Flan-T5 11B | head / torso / tail | A, H, M | LLaMA 7B 19.0, 74.4, 6.6 / 11.7, 81.0, 7.3 / 5.4, 84.8, 9.8; Vicuna 7B 16.2, 72.7, 11.0 / 9.6, 79.8, 10.6 / 4.3, 85.0, 10.7; Vicuna 13B 14.0, 55.0, 31.0 / 8.8, 62.8, 28.4 / 4.7, 70.0, 25.3; Falcon 7B 14.5, 53.8, 31.7 / 9.2, 57.9, 32.9 / 4.8, 62.0, 33.2; Flan-T5 3B 3.9, 19.7, 76.4 / 1.5, 17.1, 81.4 / 1.3, 15.5, 83.2; Flan-T5 11B 7.6, 23.7, 68.7 / 3.2, 19.9, 76.9 / 2.0, 16.5, 81.5 | Table 14 (App A.8) | The 3B row abstains on 76 to 83 percent and is right on 1 to 4 percent: the Llama 1B "no to everything" pattern; 7B base models hallucinate 74 to 85 percent at every popularity level |
| Knowledge Popularity and Boundary Perception, arXiv 2505.17537 | Llama 3 8B Instruct, Qwen2 7B, Qwen2.5 7B / 14B / 32B, ChatGPT | Wikidata QA (movies, songs, basketball) | popularity as a calibration feature | correlation; AUROC | entity popularity r 0.196 to 0.319; question-answer co-occurrence popularity up to r 0.39; MLP(confidence) AUROC 0.840 to MLP(confidence + co-occurrence) 0.877; ECE 0.356 to 0.050 | Tables 4, 5, 8 | Popularity adds about +0.04 AUROC on top of model confidence at 7 to 8B |
| Kandpal et al., arXiv 2211.08411 | BLOOM 560M to 176B, GPT-Neo family | TriviaQA, NQ vs relevant pre-training document count | | rank correlation of document counts across corpora 0.87 to 0.97 Spearman | Table 1, Figs 1, 3, 4 | Any large corpus, or Danish Wikipedia page views, is a proxy for pre-training exposure |

Pattern across 5.2 and 5.3 for the 1 to 7B range on English short-answer TriviaQA: token probability or entropy of the answer gives AUROC 0.72 to 0.84 (ASPIRE 1.5B 0.76, 2.7B 0.79; Kuhn 2.7B 0.77; INSIDE 7B 0.84; Ulmer 7B 0.79; Orgad min-logit 0.75 to 0.79), while prompted P(True) or verbalised "do I know" sits at 0.45 to 0.66 (ASPIRE 0.43 to 0.59; Kuhn 0.59 to 0.69; Xiong 0.52; Ulmer 0.52 to 0.62; Polygraph PRR below zero; Wagner 0.54 to 0.66). That is the literature version of our yes/no scaffold result and the reason the logprob run (scripts/run_logprobs.sh, scripts/confidence_gate.py) is the right next measurement.

---

## 6. Cost accounting conventions in adaptive retrieval papers

| Paper | Cost metric(s) reported | Headline numbers | Table |
|---|---|---|---|
| Mallen 2023, arXiv 2212.10511 | fraction of questions that retrieve; latency (figure); API dollars per 1000 questions | davinci-003 retrieves on 40 percent (BM25); latency minus up to 9 percent; API cost halved on PopQA, minus 15 percent on EntityQuestions; $0.46 vanilla, $2.80 BM25, $3.08 Contriever, $3.25 GenRead per 1000 q; $275 total for 14,282 q | Figs 10 to 12, App B |
| FLARE 2023, arXiv 2305.06983 | percent of sentences or steps that trigger retrieval | 30 to 60 percent of sentences on average; sweet spot 40 to 80 percent | Fig 5, App A |
| Self-RAG 2023, arXiv 2310.11511 | retrieval frequency versus threshold (figure only); training compute | 4x A100 80GB, 145,619 instances, 3 epochs; inference on 1 to 2 Quadro RTX 6000; no per-query cost | Fig 3(c) |
| CRAG 2024, arXiv 2401.15884 | TFLOPs per token; seconds per instance (generation phase only) | RAG 26.5 / 0.363 s; CRAG 27.2 / 0.512 s; Self-RAG up to 132.4 / 0.741 s; Self-CRAG up to 80.2 / 0.908 s | Table 6 |
| Adaptive-RAG 2024, arXiv 2403.14403 | Step = retrieve-and-generate iterations per query; Time relative to single-step; absolute seconds per query by class | single-step 3.08 s, multi-step 27.18 s, no-retrieval 0.35 s (FLAN-T5-XL); Adaptive-RAG Step 2.17, Time 3.60 (XL); 1.35, 2.00 (XXL); 1.03, 1.46 (GPT-3.5) | Tables 1, 3 |
| DRAGIN 2024, arXiv 2403.10081 | #Num = retrieval calls per question | 0.3 to 6.8 depending on method and dataset; SR-RAG = 1 by construction | Table 3 |
| Speculative RAG 2024, arXiv 2407.08223 | wall-clock latency per query and percent reduction | 1.17 to 1.93 s; 11.9 to 50.8 percent faster than 8x7B standard RAG | Table 2, Fig 3 |
| UAR 2024, arXiv 2406.12534 | retrieval ratio (percent of queries) | 50.1 percent on TriviaQA at 7B | Table 3 |
| Adapt-LLM 2024, arXiv 2404.19705 | percent of questions emitting RET | 82 to 84 percent on PopQA | Table 3 |
| SEAKR 2024, arXiv 2406.19215 | none in paper (20 samples per step implied) | reimplemented LMC 14.6 | Moskvoretskii Table 1 |
| Probing-RAG 2024, arXiv 2410.13339 | total retrieval calls; share of no / single / multi-step | 1,988 calls per 2,500 q (0.80); prober 5 MB | Table 2 |
| CtrlA 2024, arXiv 2405.18727 | retrieval frequency per question | 2.01 (2Wiki), 3.28 (HotpotQA) | Table 3 |
| Rowen 2024, arXiv 2402.10612 | LLM calls per question; retrieval calls per question; retrieval ratio | 5 to 8 LLM calls; 0.5 to 1.5 retrievals; 20 to 23 percent | Tables 5, 9, 10 |
| DioR 2025, arXiv 2504.10198 | retrieval count, generation count, hallucination count, token count, sentence count per question | Rc 3.0, Gc 3.0, Tc 392 to 773 tokens | Table 4 |
| Parametric RAG 2025, arXiv 2501.15915 | seconds per question; offline parameterisation about 12x document length in tokens; 4.72 MB per document | Standard RAG 3.03 s, P-RAG 2.34 + 0.32 s, FLARE 10.14 s, DRAGIN 14.60 s (LLaMA-8B, 2Wiki) | Table 4 |
| SmartRAG 2025, arXiv 2410.18141 | retrieval percentage | 0 percent when the corpus cannot help | Table 2 |
| Moskvoretskii 2025, arXiv 2501.12835 | LMC = LM calls per question including uncertainty calls; RC = retriever calls per question; reported next to InAcc | uncertainty gates LMC 1.2 to 2.0, RC 0.2 to 1.0; SeaKR LMC 14.6; RowenHybrid LMC 55 | Table 1 |
| Search-R1 / ReSearch / R1-Searcher / Search-o1 2025 | training GPUs and steps; search-call training curves only | 8x H100, 500 PPO steps; 64x H800 | Fig 2(d) etc. |
| ZeroSearch 2025, arXiv 2505.04588 | training-time search dollars (API versus GPU rental) | Google $586.7 versus simulated $17.7 to $70.8 for about 64k queries | Table 8 |
| TARG 2025, arXiv 2511.09803 | retrieval rate; added seconds per query over never-retrieve | Margin gate rate 0.001 to 0.34, +0.01 to +2.2 s | Tables 1 to 3 |
| ReaLM-Retrieve 2026, arXiv 2604.26649 | retrieval calls; latency seconds; output tokens; dollars per query at list price | 1.8 calls, 14.1 s, 9,489 tokens, $0.021 (32B, MuSiQue) | Tables 2, 4, 5 |
| CompactRAG, arXiv 2602.05728 | LLM calls per query (fixed 2); input + output tokens per query | 1.9K tokens vs IRCoT 10.2K (fetch summary, UNVERIFIED) | |
| RAGRouter-Bench, arXiv 2604.03455 | relative token cost per paradigm | LLM-only 1.0x, NaiveRAG 1.4x, IterativeRAG 3.5x; 28.1 percent saving (UNVERIFIED) | |
| BM25 wins at scale, arXiv 2607.26497 | build tokens and query tokens per question; latency | BM25 5.8K query tokens versus agent 226K (UNVERIFIED) | |
| RAG evaluation survey, Gan et al., arXiv 2504.14891 | lists TTFT, total latency, token-based API cost, infrastructure cost, cost-effectiveness ratio | no unified per-query standard proposed | |

No standard exists. The most reused convention is DRAGIN's retrieval calls per question, extended by
Moskvoretskii et al. to the pair (LM calls, retriever calls) per question, with Adaptive-RAG's
relative time as the usual latency column. For our page the defensible set is EM plus (LMC, RC),
mean generated tokens, and measured seconds per row on the GTX 1060; no paper above reports that for
1 to 4B quantised models. Our measured seconds per row (RESULTS.md): closed-book 0.3 to 1.2 s (Mimir
6.0 s, HRM loop), retrieve 1.3 to 3.7 s (Mimir 9.3 s), agentic 3.7 s (Qwen 3B) and 5.9 s (Gemma 4B).

---

## 7. What our numbers look like next to these

Same-shape tasks only: short-answer factual questions about one entity, one model call per condition
plus at most one retrieval, strict or near-strict string scoring. Every mismatch is listed under each
placement. Nothing below is a claim of superiority over a published system; the point is that our
numbers land where the literature says they should, which is what makes the study credible.

### 7.1 Closed-book: our 0.8 to 5.6 EM (1 to 4B) and 22.5 EM (70B) are the expected floor

| Ours | Nearest published | Mismatches |
|---|---|---|
| Llama 3.2 1B 0.8; Qwen 2.5 3B 3.0; Llama 3.2 3B 4.1; Gemma 3 4B 5.6; Mimir 1B 5.6 (theirs 9.6) | Mimir report Table 9 on the same 592 rows: Gemma 3 1B 1.4, Qwen 3.5 0.8B 0.7, Qwen 3.5 2B 2.5, SmolLM3 3B 2.2, Qwen 3.5 4B 4.7, Gemma 4 E2B 5.6, Mimir 9.6, Munin-Apertus 8B 12.5 | Identical task and scorer; their models are unquantised bf16 through Inspect AI, ours are Q6 to Q8 GGUF through llama.cpp; our Mimir runs causal-only (GROUP-PAPERS.md 3.2) |
| same | Gopher Table A15 prompted 0-shot NQ: 1B 2.4, 7.1B 6.1, 280B 10.1 (64-shot 8.1 / 16.5 / 28.2); Llama 65B 0-shot strict EM NQ 5.2 (RA-DIT Table 2); Qwen2.5-3B-Instruct 0-shot strict EM NQ 10.6 / PopQA 10.8 (Search-R1 Table 2); Llama-3.2-3B base PopQA 7.4 (ZeroSearch Table 3); SimpleQA Gemma 3 4B 4.0, 1B 2.2 (Gemma 3 Table 6) | English; NQ and PopQA have multi-alias gold; SimpleQA is LLM-graded; base versus instruct models differ; our 0-shot Danish prompt asks for a bare answer, which strict EM rewards |
| Llama 3.3 70B 22.5 EM (group's predictions rescored) | SimpleQA Llama-3.3-70B 20.9 (phi-4 Table 1); Llama 3.1 70B NQ 5-shot F1 51.3 (OLMo 2 Table 6), TriviaQA-Wiki 5-shot EM 89.8 (Meta card); Llama 65B NQ 0-shot 5.2 / 5-shot 31.6 strict EM (RA-DIT); MultiLoKo frontier average 34 EM on locally sourced questions (Table 2, Danish not included) | The Danish culture canon is about as hard for a 70B model as SimpleQA is, and far harder than TriviaQA; 0-shot strict EM at 70B is 5 to 30 on English sets depending on shots and aliases, so 22.5 is inside the band |

Reading: closed-book DAISY is a long-tail entity benchmark. Mallen's tail buckets stay at 0.05 to 0.15
regardless of size (Fig 5); Kandpal shows scale cannot reach the tail (10^18 parameters extrapolated);
Head-to-Tail gives 7B base models 5 percent accuracy and 85 percent hallucination on tail entities
(Table 14). Our 1 to 4B closed-book numbers are that tail, in Danish.

### 7.2 One lookup, always: our 15 to 31 EM sits where a 40 percent retrieval hit rate predicts

| Ours | Nearest published | Mismatches |
|---|---|---|
| retrieve (shaped query, top-3 da.wikipedia intros, gold-in-context 40.4 percent): Llama 1B 15.2, Mimir 26.5, Qwen 3B 27.9, Llama 3B 28.2, Gemma 4B 31.1; reading fidelity given a hit 0.37 to 0.73 | PopQA Contriever top-1 (recall@1 0.42): GPT-Neo 1.3B 0.335, 2.7B 0.355, GPT-J 6B 0.37, NeoX 20B 0.38 (Mallen Fig 13, acc(contains)); Search-R1 RAG Qwen2.5-3B-Instruct E5 top-3: NQ 34.8 / PopQA 38.7 strict EM; ZeroSearch RAG Llama-3.2-3B base with 5 Google docs: NQ 30.0 / PopQA 26.4; Adaptive-RAG single-step FLAN-T5-XL 3B BM25: NQ 37.8 / TQA 53.6 / SQuAD 27.8 EM; In-context RALM LLaMA-7B + 2 DPR docs: NQ 28.0 EM; Self-RAG Llama2-7B + top-5 plus web: PopQA long-tail 38.2 acc(contains); SmartRAG Flan-T5-large 780M + Bing: PopQA 34.4 EM; RetrievalQA TinyLlama 1.1B 28.2 | Retriever: ours is a title-match intro lookup with a heuristic query, theirs dense or BM25 over full passages or live web; k = 3 intros of about 600 chars versus 1 to 5 passages of 100 words; language; scoring (containment for PopQA and Self-RAG); their base models are 15-shot (Mallen) or fine-tuned (Adaptive-RAG uses FLAN-T5); ours 0-shot instruct |
| same | Negative results at our size: Probing-RAG Gemma-2B single-step BM25 lowers NQ 15.0 to 11.4 and TQA 37.4 to 19.6 (Table 1); Pandey 2026 Qwen2.5-3B NF4 dense retrieval over 2 percent of Wikipedia (hit@5 16 percent) lowers EM by 1.9 pp (Table 4); TARG Qwen2.5-7B always-retrieve lowers TQA 60.8 to 57.6 (Table 1) | Our gain is positive because the hit rate (40 percent) exceeds the closed-book rate (3 to 6 percent) by an order of magnitude; where closed-book is 40 to 60 or hits are 10 to 16 percent, one always-on lookup hurts. Our reading-fidelity split (0.03 EM when the gold is absent) shows the distraction cost is small in our regime |
| Gain in points: +14 (Llama 1B), +21 (Mimir), +25 (Qwen 3B), +24 (Llama 3B), +26 (Gemma 4B) | In-context RALM +17.7 to +19.0 (NQ, 7B to 33B); Search-R1 RAG +24.2 NQ / +27.9 PopQA (3B); Self-RAG +23.5 PopQA (7B); RETRO fine-tuned +15.1 NQ; RA-DIT REPLUG 0-shot +23.6 NQ (65B); Adaptive-RAG +23.6 NQ (3B) | Same magnitude band (+15 to +28) across sizes, retrievers and languages; ours is at the top of the band because the closed-book base is near zero |

### 7.3 Oracle subject query: our 39 to 68 EM is the passage-given regime

| Ours | Nearest published | Mismatches |
|---|---|---|
| retrieve-oracle (subject name as query, gold-in-context 78.7 percent): Llama 1B 39.2, Mimir 60.6, Qwen 3B 62.8, Llama 3B 64.4, Gemma 4B 67.9 | EuroEval MultiWikiQA-da (Danish Wikipedia passage given, EM secondary): Mimir 65.2 to 66.3, Qwen3.5-2B 54.7, Llama-3.2-3B-Instruct 52.6, Qwen3.5-4B 39.5, Llama-3.3-70B 41.7, best 70.5 (Ministral-3-14B-Base); Mimir report Table 9 MultiWikiQA: Mimir 66.8, Gemma 4 E2B think 59.3, Qwen 3.5 4B 57.1, Gemma 3 1B 42.6 | Closest match in the whole document: Danish, Wikipedia passage, short answer, EM, same model sizes. Their gold is guaranteed in the passage (ours 78.7 percent), their answers are verbatim spans (ours include years and numbers that may need normalisation), 4-shot versus our 0-shot |
| same | Lost in the Middle oracle passage GPT-3.5 88.3 / Claude 76.1 acc(contains); Adapt-LLM gold passage SQuAD 89.42 EM (7B fine-tuned); FRAMES oracle articles Gemini 1.5 Pro 0.729 (multi-hop); Atlas 3B 64-shot NQ 41.3 EM (fine-tuned, 40 passages); Pandey 2026 oracle on unknown questions Qwen2.5-3B 12.8 percent | Frontier or fine-tuned readers reach 76 to 89 with a guaranteed passage; our 60 to 68 for 3 to 4B with a 79 percent hit rate implies a reading efficiency of about 0.8, consistent with the reading-fidelity column (0.64 to 0.73). Pandey's 12.8 is the outlier and is measured on the subset the model got wrong closed-book, which is 94 to 97 percent of our questions anyway, so the setups are not equivalent |

### 7.4 Agentic single call: our 40 EM for Gemma 3 4B and Qwen 2.5 3B is level with RL-trained 3B search agents on English

| Ours | Nearest published | Mismatches |
|---|---|---|
| agentic (model writes one SEARCH line, top-3 intros, then answers; LMC 1.93 and 2.0, RC 0.93 and 1.0): Gemma 3 4B 39.9 (553 calls, first hit = subject 48 percent), Qwen 2.5 3B 40.0 (592 calls, 52 percent); beats our own heuristic query (31.1 / 27.9) | Search-R1 Qwen2.5-3B (RL-trained, E5 top-3, up to 4 turns): instruct NQ 34.1 / TQA 54.5 / PopQA 37.8; base 40.6 / 58.7 / 43.5; plain one-call RAG 34.8 / 54.4 / 38.7 (Table 2); ZeroSearch Qwen-2.5-3B with Google 5 docs: RL-trained 41.4 to 43.0 NQ, 41.4 to 44.8 PopQA; untrained prompted agent "RAgent" 15.2 NQ / 6.6 PopQA, below plain RAG (Table 3); Adapt-LLM 7B 36.77 PopQA; BFCL V4 web-search column Llama-3.2-3B 1.0, Gemma-3-4b 1.0, Qwen3-4B 3.0, frontier 80 to 85; Jan-nano (Qwen3-4B fine-tune) SimpleQA 80.7 to 83.2 with Google plus page scrape, plain Qwen3-4B with the same tools 59.2 | Theirs is English, dense or web retrieval over full passages, up to 4 or many calls, and (Search-R1, ZeroSearch, Jan-nano) reinforcement-learned; ours is a single Danish Wikipedia title query with no training. Two honest readings: (a) an untrained 3 to 4B instruct model writing one query lands at the same 40 EM that RL agents reach on single-hop English sets, and (b) that is because on single-hop questions RL agents barely beat one-call RAG (34.1 vs 34.8 NQ), so the headroom is in the retriever, not the policy. ZeroSearch's untrained RAgent rows (15.2 NQ) show that free-form agent prompts often fail at 3B, which matches our Llama 3.2 1B / 3B and Mimir never emitting SEARCH |
| Llama 3.2 1B, Llama 3.2 3B and Mimir 1B: 0 of 592 calls in the free-form agentic prompt; with the yes/no scaffold 592, 72 and 182 calls | ZeroSearch RAgent below RAG at 3B; BFCL web search 0.0 to 1.0 for Llama 3.2 1B / 3B; Parametric RAG FLARE and DRAGIN collapse below 8B (Table 1); Mallen: models under 10B "almost always retrieve" under the popularity rule | The format hurdle (emit a tool line) and the decision hurdle are separate; the scaffold removes the first. No published number isolates the two at 1B |

### 7.5 Knowing when to look: the yes/no probe matches the literature on prompted self-knowledge

| Ours | Nearest published | Mismatches |
|---|---|---|
| Of the questions each model then got wrong, the share that claimed to know: Mimir 69 percent, Llama 3B 88 percent, Gemma 4B 11 percent, Qwen 3B 1 percent, Llama 1B 0 percent (said no to everything). Call precision is 0.95 to 0.99 everywhere because closed-book accuracy is 3 to 6 percent | Prompted P(True) or verbalised confidence at 1.5B to 13B: ASPIRE 0.43 to 0.59 AUROC, Kuhn 0.59 to 0.69, Ulmer 0.52, Xiong Vicuna 13B 0.525 with confidences "predominantly 80 to 100 percent", Wagner Qwen2.5 3B verbalised P(IK) 0.59, Polygraph P(True) PRR below zero; Kadavath: zero-shot P(True) "close to 50%", small models "trivially calibrated"; Head-to-Tail Flan-T5 3B abstains on 76 to 83 percent; Yin: instruction tuning moves hedging more than size below 7B | We report shares, not AUROC, and we have no logprob run yet; Kadavath's models are 800M to 52B base models with 20-shot prompts; our probe is 0-shot Danish |
| Decision problem is degenerate at 3 to 6 percent closed-book: "always search" is near-optimal | Mallen: adaptive gain "much smaller" under 10B because they almost always retrieve; Adapt-LLM 7B asks on 82 to 84 percent of PopQA; Probing-RAG Gemma-2B 0.80 calls per question; Moskvoretskii oracle gate on TriviaQA (closed-book 0.636) needs only 36 percent retrieval | The interesting gate lives where closed-book is 40 to 60 percent (7B English or 70B Danish); at our operating point the literature agrees the gate is worth little. Say so on the page |
| Next measurement (run_logprobs.sh, confidence_gate.py): AUROC of mean, min, first-token and sum logprob for closed-book correctness | Targets from English short-answer QA: token probability or entropy 0.72 to 0.84 at 1.5B to 7B (ASPIRE 0.76 / 0.79, Kuhn 0.77, INSIDE 0.84, Orgad min-logit 0.75 to 0.79, Ulmer 0.79); Moskvoretskii entropy as retrieval trigger 0.62 to 0.74 at 8B; popularity adds about +0.04 (arXiv 2505.17537) | With 17 to 33 correct closed-book answers per model out of 592, our AUROC will have wide intervals; report them |

### 7.6 Cost

Our rows are (LMC, RC) = (1, 0) closed-book, (1, 1) retrieve, (1.93 to 2.0, 0.93 to 1.0) agentic,
(2.31 to 3.0, 0.31 to 1.0) scaffold, at 0.3 to 9.3 s per row on a GTX 1060 (RESULTS.md). Every
iterative method in Section 2.4 sits at LMC 2.7 to 55 and RC 1.4 to 7.3 (Moskvoretskii Table 1),
Adaptive-RAG at Step 2.17 and 3.6x single-step time, DRAGIN at 2.5 to 4.8 retrievals per question.
Our agentic condition is the cheapest configuration in the table that lets the model choose the
query, and no paper reports per-row seconds for quantised 1 to 4B models on consumer hardware.

### 7.7 What we cannot claim

No published system has run DAISY with retrieval, so there is no record to beat and no external
number to match; our comparisons are all to English or to the group's closed-book numbers. Our
scoring is stricter than PopQA, Self-RAG, CRAG and SimpleQA (containment or LLM judge), which flatters
their numbers relative to ours by an unknown amount; MultiWikiQA-da and the Mimir report use EM like
us. Our models are quantised and our Mimir port is causal-only, so our Mimir closed-book 5.6 is not
a replication of the group's 9.6. Our retrieval is a title lookup on da.wikipedia intros, not a
dense index, so "retriever" comparisons are by hit rate only. Our 592 questions are the public
subset; the paper's Table 2 is on 741.

---

## 8. Records we could try to beat on identical terms

"Identical terms" means: same public question set, same retrieval inputs (or none), same metric
script, a model that fits a 6 GB GTX 1060 through llama.cpp or 8-bit transformers, and a published
row to sit next to. Ordered by value per hour.

| Benchmark and setting | Published row to sit next to | What we would run | Feasibility on the 1060 | Status of identical terms |
|---|---|---|---|---|
| DAISY 592, closed-book, official prompt, greedy, EM (Mimir report Table 9 protocol) | 1 to 4B ceiling 9.6 (Mimir 1B), 5.6 (Gemma 4 E2B), 4.7 (Qwen 3.5 4B); 8B 12.5 (Munin-Apertus); 70B 22.5 (our rescoring) | Already run: 0.8 to 5.6. Fixing the prefix-LM attention for Mimir (transformers fp16 on GPU, token_type_ids) is the one closed-book item that could move: target 9.6 | Yes; the transformers path needs an sm_61 torch build (PLAN.md) | Identical except quantisation; no retrieval condition exists in print, so every retrieval row of ours is a first, not a record |
| DAISY 592 with a Danish Wikipedia passage (our retrieve-oracle) | none published; nearest is MultiWikiQA-da EM (Mimir 66.3, Llama-3.2-3B 52.6, best 70.5) | Already run: 39 to 68. Could add k and snippet-length sweeps (IDEAS 4) | Yes | Not identical to MultiWikiQA (hit 79 percent vs 100, 0-shot vs 4-shot); report side by side, not as a beat |
| EuroEval MultiWikiQA-da (2,048 q, 4-shot, F1 / EM) via the EuroEval CLI against an OpenAI-compatible llama-server | best under 5B: Mimir 79.94 F1 / 66.25 EM; Llama-3.2-3B-Instruct 70.23 / 52.62; Qwen3.5-4B 46.99 / 39.53; Llama-3.3-70B 70.18 / 41.74; overall best Olmo-3-32B 83.76 / 69.88 | Gemma 3 4B it and Qwen 2.5 3B Instruct, which are missing from the board (only a q4_0 partial row for Gemma) | Yes; EuroEval already lists a q4_0 GGUF row via ollama, so a llama.cpp backend is accepted | Identical terms by construction; realistic outcome: fill two gaps, possibly beat Llama-3.3-70B's 41.74 EM with a 3 to 4B model (Mimir already does). The group's own dfm-evals Multi Wiki QA task (0-shot, 32 tokens) is the second protocol; see GROUP-PAPERS.md fact 5 |
| EuroEval Danish Citizen Tests (525 MCQ) and Danske Talemaader (808 MCQ), MCC | best under 5B: Qwen3.5-4B 77.30 and 55.39; Llama-3.2-3B 44.55 and 18.45; gemma-3-4b-it q4 53.91 and 44.03 | Gemma 3 4B and Qwen 2.5 3B (missing); plus an off-leaderboard "with da.wikipedia lookup" variant to see whether a lookup lifts MCQ knowledge the way it lifts DAISY | Yes | Identical for the plain runs; the lookup variant is a new condition, not comparable to the board |
| PopQA long-tail 1,399 with Self-RAG's released passages (eval_data/popqa_longtail_w_gs.jsonl, Contriever top-10 plus web, "contexts" field), metric match = acc(contains), ndocs 5 or 10 | untrained: Llama2-7B + ret 38.2, Alpaca-7B 46.7, Llama2-chat-13B 51.8, Ret-ChatGPT 50.8, RAG (LLaMA2-hf-7b, CRAG Table 1) 50.5; trained: Self-RAG 7B 54.9, CRAG 59.8, Self-CRAG 61.8, CtrlA 61.8, Speculative RAG 57.54 | Gemma 3 4B, Qwen 2.5 3B, Llama 3.2 3B and 1B, Mimir 1B, each with the same passages prepended, 0-shot, and our agentic re-query on top of the released web passages if the file carries them | Yes: 1,399 rows at 2 to 6 s = 1 to 2.5 h per model; passages already retrieved, no index needed. The README confirms each file "already comes with retrieved documents" | Identical retrieval inputs and metric script (run_short_form.py, metric match); model size 1 to 4B versus 7B; plausible target: beat the untrained 7B and 13B rows (38.2 to 51.8) with an untrained 4B, i.e. the English mirror of the DAISY story |
| TriviaQA unfiltered 11,313 with Self-RAG's released passages (triviaqa_test_w_gs.jsonl), acc(contains) | untrained Llama2-7B + ret 42.5, Alpaca-7B 64.1, Llama2-chat-13B 59.8, Ret-ChatGPT 65.7; Self-RAG 7B 66.4 / 13B 69.3; CtrlA 76.4 | same models | Yes but long: 11,313 rows at about 4 s = 12 h per model; run one or two models overnight, or the first 2,000 rows with a stated subset | Identical inputs and metric; a stated subset breaks identity, so run the full file for at least one model |
| Adaptive-RAG 500-question NQ, TriviaQA and SQuAD sets with BM25 (Elasticsearch 7.10.2 over the released Wikipedia index of 21,015,324 documents; processed_data.tar.gz and predictions.tar.gz), EM / F1 / Acc / Step / Time | FLAN-T5-XL 3B: no retrieval NQ 14.20 / TQA 25.00 / SQuAD 3.60; single-step 37.80 / 53.60 / 27.80; Adaptive-RAG 37.80 / 52.20 / 26.80 (Step 1.00 / 1.23 / 1.37); FLAN-T5-XXL single-step 41.40 / 56.00 / 28.80; GPT-3.5 no retrieval 39.80 / 64.00 (Table 8); Probing-RAG Gemma-2B on the same corpus: single-step NQ 11.4 / TQA 19.6, Probing-RAG 21.6 / 41.8 | Gemma 3 4B and Qwen 2.5 3B in three conditions: closed, single-step BM25 top-k (their k), and our agentic single query; report Step and relative Time exactly as they do | Yes if predictions.tar.gz carries the BM25 outputs for the test sets (then no Elasticsearch needed); otherwise Elasticsearch on CPU over 21M documents needs about 20 to 30 GB disk and a few hours to index, RAM 16 GB is enough | Identical question sets, retriever and metric script; the model differs (instruct decoder vs FLAN-T5), which is the point. Plausible target: beat single-step 37.80 NQ EM at 3 to 4B with one call, and beat Probing-RAG's 21.6 / 41.8 with an untrained gate (our scaffold) |
| Search-R1 / FlashRAG protocol: NQ 3,610, TriviaQA 11,313, PopQA 14,267 with E5-base-v2 top-3 over the 2018 Wikipedia dump, strict EM | Qwen2.5-3B-Instruct direct 0.106 / 0.288 / 0.108; RAG 0.348 / 0.544 / 0.387; Search-R1-instruct 0.341 / 0.545 / 0.378; Search-R1-base 0.406 / 0.587 / 0.435; 7B RAG 0.349 / 0.585 / 0.392 | Qwen 2.5 3B Instruct (same model) closed, RAG, agentic | Borderline: the prebuilt E5 flat index over 21M passages is tens of GB and needs RAM or GPU to search; FlashRAG's BM25 index is the feasible substitute, which breaks identity (their Table 3 rows are E5). The RAG rows of ZeroSearch use live Google, which is not reproducible | Not identical unless the E5 index can be served from disk; list as "same test files, different retriever" if run with BM25 |
| lm-eval-harness TriviaQA 0-shot EM, no evidence (arXiv 2509.02225 Table 6) | Llama-3.2-1B 0.2509, Llama-3.2-3B 0.5088, Qwen2.5-3B 0.4242, SmolLM2-1.7B 0.3879, gemma-2-2b 0.5080, Llama-3.1-8B 0.6170 | Reproduce the closed-book rows for our four models with 8-bit transformers, then add the English Wikipedia intro lookup as a new column | Yes (harness runs on 8-bit HF models; 17,944 dev questions at 0.3 to 1 s each) | Closed-book reproduction is identical; the lookup column is a first, comparable to the RAG rows above only by hit rate |
| SimpleQA 4,326 with the official simple-evals grader | Gemma 3 4B 4.0, 1B 2.2 (Gemma 3 Table 6); with tools: plain Qwen3-4B + Google MCP search and scrape 59.2, Jan-nano 4B 80.7 / 83.2 (arXiv 2506.22760 Table 1); gpt-4o-mini-search-preview 88 | Gemma 3 4B and Qwen 2.5 3B closed-book (reproduce 4.0) and with an English Wikipedia intro lookup, both shaped and agentic | Yes for generation (4,326 rows at about 5 s = 6 h per condition); grading needs the GPT-4o classifier prompt through the API (a few dollars per run) | Closed-book identical; with-search rows differ in tool (Wikipedia intros vs Google plus scrape) and in training (Jan-nano is fine-tuned). A Wikipedia-only 4B SimpleQA number does not exist in print |
| FRAMES 824 (naive prompt rows exist for our size class) | Llama3.2-3B 0.115, Qwen2.5-3B 0.095 naive; Gemini 1.5 Pro BM25 n_doc 4 0.474, oracle 0.729, multi-step 0.66 | our models with one or two Wikipedia lookups | Yes for generation; needs the LLM autorater | Multi-hop and LLM-graded; low priority |
| Calibration: TriviaQA AUROC from token logprobs, 1.5B to 2.7B (ASPIRE Table 1) | GPT2-XL 1.5B entropy 0.762, OPT-2.7B 0.789; P(True) 0.45 to 0.59 | llama-server logprobs for our four models on DAISY (running: run_logprobs.sh) and on the lm-eval TriviaQA dev set | Yes | Same method (answer log-probability), different models and language; DAISY AUROC is a first in Danish |
| Head-to-Tail 18,171 (head / torso / tail) | Flan-T5 3B 3.9 / 1.5 / 1.3 accuracy with 76 to 83 percent abstention; LLaMA 7B 19.0 / 11.7 / 5.4 | our models closed-book and with lookup, by popularity tercile | Generation yes; needs the ChatGPT judge | LLM-judged; medium priority, but the popularity split is exactly our subject-popularity retrieval trigger |

The two runs that give the most for the least: (1) PopQA long-tail with Self-RAG's released passages,
because the inputs are identical to a well-cited table and a 4B beating the untrained 7B and 13B rows
is the English twin of the DAISY headline; (2) EuroEval MultiWikiQA-da for Gemma 3 4B and Qwen 2.5 3B,
because it is the group's own reading task, the board has a hole where our models should be, and
a 3 to 4B model above Llama-3.3-70B's 41.74 EM is already the norm there.

---

## 9. Not found, unverified, and the bibliography

Not found in print as of 4 Sep 2026: any DAISY result with retrieval; any Danish RAG benchmark with
EM or F1; SimpleQA or PopQA numbers for Llama 3.2 3B, Qwen 2.5 3B or Gemma 3 4B with a Wikipedia-only
tool; a 2024 to 2026 table in which a 1 to 4B model plus retrieval beats a 70B model closed-book on
NQ, TriviaQA or PopQA (the nearest are figures in Lazaridou 2022, Mallen 2023, MassiveDS 2024 and the
Atlas Table 19 versus Table 8 comparison); Llama 3.3 70B TriviaQA or NQ numbers from Meta; Gemini
grounding or Anthropic web-search accuracy pairs; BFCL V4 rows for Qwen2.5-3B / 7B, Phi-4-mini, GPT-4o.

Unverified (do not quote): all PopQA per-model bars (Figs 4, 7, 9, 10, 13, 14) beyond the text
anchors 35, 25, +7 and 46.5; Kadavath Figs 4, 14, 18, 31 readings (Table 1 is exact); Farquhar
per-model AUROC (Supplementary not fetched); SmolLM2 Table 4 metric; Self-RAG Fig 3(c) and FLARE
Fig 5 curves; Search-R1, ZeroSearch and Search-o1 test-set sizes; B1ade Table 2 setup; Soudani Table
3 retriever; SEB per-task Danish retrieval scores; Danoliteracy GPT-4 and Claude Opus raw accuracies;
the segiITU Talemaader zero-shot setup; Exa and Linkup vendor numbers; o4-mini BrowseComp 28.3;
GPT-4.5 SimpleQA hallucination rate; Claude Opus 4.5 and Sonnet 4.5 BrowseComp via vellum.ai; Kimi-
Researcher, GPT-5 Pro, Gemini 2.5 Deep Research and Grok 4 Heavy BrowseComp; CompactRAG, RAGRouter-
Bench, BM25-at-scale and RAGate numbers (fetch summaries only); Kang 2024 figure values; Madhusudhan
Table 1.

Bibliography (arXiv id, venue where known)

Danish and Nordic: 2601.19930 DAISY (SDU, 2026); 2608.13517 DFM Mimir v1 (2026); 2304.00906 ScandEval
(NoDaLiDa 2023); 2406.13469 Encoder vs Decoder (2024); 2509.04111 MultiWikiQA (2025); 2512.04799 DaLA;
2506.19468 Winogrande-da; 2412.12956 SnakModel (NoDaLiDa 2025); 2504.02403 DaKultur; 2410.22839
Danoliteracy (NoDaLiDa 2025); 2305.01957 NorQuAD (NoDaLiDa 2023); 2504.10356 MultiLoKo; 2406.02396
SEB (NeurIPS 2024 D&B); 2605.27220 Coverage Illusion (lex.dk); 2305.12987 GPT-SW3; 2404.01856 Poro;
2603.16406 NQiI.

English QA and retrieval: 2212.10511 PopQA (ACL 2023); 2211.08411 Kandpal (ICML 2023); 2308.10168
Head-to-Tail (NAACL 2024); 2002.08910 Roberts (EMNLP 2020); 2002.08909 REALM (ICML 2020); 2007.01282
FiD (EACL 2021); 1911.00172 kNN-LM (ICLR 2020); 2112.04426 RETRO (ICML 2022); 2112.11446 Gopher;
2208.03299 Atlas (JMLR 2023); 2301.12652 REPLUG (NAACL 2024); 2310.01352 RA-DIT (ICLR 2024);
2302.00083 In-context RALM (TACL 2023); 2203.05115 Lazaridou; 2407.12854 MassiveDS (NeurIPS 2024);
2302.13971 LLaMA; 2307.09288 Llama 2; 2407.21783 Llama 3; 2310.06825 Mistral 7B; 2403.08295 Gemma 1;
2408.00118 Gemma 2; 2503.19786 Gemma 3; 2412.15115 Qwen2.5; 2404.14219 Phi-3; 2503.01743 Phi-4-mini;
2412.08905 phi-4; 2502.02737 SmolLM2; 2501.00656 OLMo 2; 2509.02225 Towards Fundamental LMs;
2310.11511 Self-RAG (ICLR 2024); 2305.06983 FLARE (EMNLP 2023); 2403.14403 Adaptive-RAG (NAACL 2024);
2403.10081 DRAGIN (ACL 2024); 2401.15884 CRAG; 2407.08223 Speculative RAG; 2310.04408 RECOMP (ICLR
2024); 2311.09210 Chain-of-Note; 2307.03172 Lost in the Middle (TACL 2024); 2405.13576 FlashRAG;
2402.16457 RetrievalQA; 2312.05934 Ovadia; 2403.01432 Soudani; 2503.09516 Search-R1 (COLM 2025);
2505.04588 ZeroSearch; 2503.05592 R1-Searcher; 2503.19470 ReSearch; 2501.05366 Search-o1; 2406.19215
SEAKR; 2406.12534 UAR; 2310.05002 SKR (EMNLP 2023 Findings); 2404.19705 Adapt-LLM; 2410.13339
Probing-RAG (NAACL 2025 Findings); 2405.18727 CtrlA (ACL 2025 Findings); 2402.10612 Rowen (SIGIR-AP
2025); 2504.10198 DioR (ACL 2025); 2501.15915 Parametric RAG (SIGIR 2025); 2410.18141 SmartRAG (ICLR
2025); 2407.21712 RAGate (NAACL 2025 Findings); 2511.09803 TARG; 2501.12835 and 2505.04253
Moskvoretskii et al.; 2604.26649 ReaLM-Retrieve; 2603.11513 Pandey; 2607.27506 B1ade; 2504.01018
Self-Routing RAG; 2509.12765 InfoGain-RAG; 2602.05728 CompactRAG; 2604.03455 RAGRouter-Bench;
2607.26497 BM25 at scale; 2504.14891 RAG evaluation survey.

Industry evaluations: 2411.04368 SimpleQA; 2509.07968 SimpleQA Verified; 2504.12516 BrowseComp;
2508.06600 BrowseComp-Plus; 2409.12941 FRAMES; 2507.06261 Gemini 2.5 report; 2506.22760 Jan-nano;
2507.02592 WebSailor; 2510.24701 Tongyi DeepResearch; 2511.11793 MiroThinker; 2508.07976 ASearcher;
2406.12045 tau-bench; 2506.07982 tau2-bench; BFCL leaderboard gorilla.cs.berkeley.edu; OpenAI system
cards (o3 and o4-mini, GPT-4.5, GPT-5) at cdn.openai.com; github.com/openai/simple-evals.

Calibration and abstention: 2207.05221 Kadavath; 2205.14334 Lin; 2306.13063 Xiong (ICLR 2024);
2305.18153 SelfAware; 2302.09664 Kuhn (ICLR 2023); Farquhar et al., Nature 630, 625 to 630 (2024);
2311.09677 R-Tuning; 2403.05612 Kang; 2403.05973 APRICOT; 2410.02707 Orgad (ICLR 2025); 2402.03744
INSIDE (ICLR 2024); 2311.07383 and 2406.15627 LM-Polygraph (TACL 2025); 2310.11689 ASPIRE;
2406.08391 Kapoor (NeurIPS 2024); 2607.08456 Wagner; 2501.03991; 2505.23854; 2602.04577; 2605.02241;
2604.05779; 2006.09462 Kamath (ACL 2020); 2407.18418 Wen (TACL 2025); 2506.09038 AbstentionBench;
2405.01563 Yadkori; 2407.16221 Madhusudhan; 2608.22228 GRAB-RAG; 2603.21172; 2605.25394;
2505.17537 Knowledge Popularity.
