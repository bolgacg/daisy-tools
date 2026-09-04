# Ceilings and readers: how far a small system can go on DAISY, by the numbers

Written 4 Sep 2026 for the DAISY-with-tools program. Question from Bo: how do we get above 90 percent
exact match on the 592 public DAISY questions without cheating, with a simple method, and is it possible
without a bigger model. This file collects the published ceilings (reader accuracy given the passage,
retrieval recall, reranking gains, page finding, query rewriting, fine-tuning gains) with exact numbers
and citations, then gives a verdict. Every number is copied from the cited table; "contains" marks a
lenient metric (gold string anywhere in the output), "EM" marks SQuAD-style exact match after
normalisation. Our own numbers come from results/RESULTS.md and PROGRAM.md (4 Sep 2026).

The answer in four lines. The published passage-given ceiling for entity questions is 85 to 90 EM, and it
is reached three ways: a 300M encoder fine-tuned on about 90k in-language examples, a 7B decoder
fine-tuned on SQuAD, or an untuned 70B-plus decoder. No published Danish passage-given EM exceeds 70.5
at any size, and the human EM on every human-written English set is 77 to 87. DAISY at 90 EM would
therefore need page finding, passage coverage and reading each above 96.5 percent at once; 80 is
credible with a 4B model and a rerank step, 85 needs an 8B reader or a fine-tuned extractive encoder,
90 is not credible without benchmark-specific priors.

## 0. The arithmetic first

DAISY EM factorises as: P(the right page is found) times P(the answer is inside the text shown to the
reader, given the page) times P(the reader extracts and formats it, given it is shown). Our measurements
of the three factors today:

| factor | our best measurement | source |
|---|---|---|
| right page found by a model-written query (first hit is the subject page) | 0.48 to 0.57 of calls; 20 to 26 percent of queries return nothing and fall back to the rule query | RESULTS.md "Can the model ask" |
| answer inside the top-3 intros when the subject name is the query (answer recall@3) | 0.787 | RESULTS.md retrieval ceiling |
| reader EM given the oracle query (subject name), all 592 | Gemma 3 4B 0.679, Llama 3.2 3B 0.644, Qwen 2.5 3B 0.628, Mimir 1B 0.698 (fixed attention, first 278 rows), Llama 3.2 1B 0.392 | RESULTS.md, PROGRAM.md 16:45 |
| implied reader EM given the answer is present (0.679 / 0.787) | about 0.86 for Gemma 3 4B, 0.82 Llama 3B, 0.80 Qwen 3B, 0.50 Llama 1B | derived |
| lenient minus strict gap in the oracle condition (format headroom) | Gemma 4.1 points, Llama 3B 7.4, Qwen 4.4, Mimir 4.4, Llama 1B 18.7 | RESULTS.md |

Two consequences. First, the 3 to 4B readers already read at about 0.86 EM when the answer is in front
of them, which is the SQuAD-human EM band (Section 1.4). The reader is not the bottleneck. Second, the
two retrieval factors multiply to at most 0.787 with the oracle query and to roughly 0.45 with model
queries, so every point above 70 has to come from finding the page more often and from showing more of
the page than its introduction. To reach 90 overall, each of the three factors must exceed 0.965. No
published system achieves that on any open-domain QA set: the best end-to-end EM on NaturalQuestions is
64.0 (Atlas 11B, arXiv 2208.03299, Table 19) and on TriviaQA 84.7 (Atlas, unfiltered, Table 8), with
retrievers and readers trained on tens of thousands of in-domain examples.

## 1. Reader accuracy given the passage, as a function of model size

### 1.1 Extractive encoders, fine-tuned on the training split (English unless stated)

| model | parameters | SQuAD 1.1 dev EM / F1 | SQuAD 2.0 dev EM / F1 | source |
|---|---|---|---|---|
| BERT-base | 110M | 80.8 / 88.5 | | arXiv 1810.04805, Table 2 |
| BERT-large | 340M | 84.1 / 90.9 | 78.7 / 81.9 | same, Tables 2 and 3 |
| RoBERTa-large | 355M | 88.9 / 94.6 | 86.5 / 89.4 | arXiv 1907.11692, SQuAD table |
| DeBERTa-large | 400M | 90.1 / 95.5 | 88.0 / 90.7 | arXiv 2006.03654, Table 2 |
| DeBERTa-base | 140M | 87.2 / 93.1 | 83.1 / 86.2 | same, Table 3 |
| DeBERTa-v3-large | 435M | | 89.0 / 91.5 | arXiv 2111.09543 |
| DeBERTa-v3-base | 184M | | 85.4 / 88.4 | same |
| DeBERTa-v3-small | 143M | | 80.4 / 82.9 | same |
| deepset/deberta-v3-large-squad2 | 435M | | 87.61 / 90.75 | model card |
| deepset/xlm-roberta-large-squad2 (multilingual) | 560M | | 79.46 / 83.79; German XQuAD 61.51 / 78.80; German MLQA 49.35 / 66.16 | model card |
| deepset/xlm-roberta-base-squad2 (multilingual) | 278M | | 73.92 / 77.14; German XQuAD 48.74 / 62.55 | model card |
| timpal0l/mdeberta-v3-base-squad2 (multilingual) | 278M | | 80.88 / 84.01 | model card |
| XLM-R large, MLQA zero-shot transfer, 7-language average | 560M | MLQA EM 52.7 / F1 70.7 (German 53.6 / 68.5) | | arXiv 1911.02116, Table 3 |

Reading: with 88k in-language training questions, a 110M encoder reads at 81 EM and a 355M encoder at
89 EM. Transferred zero-shot to another language, the same encoders lose 15 to 25 EM points (XLM-R large
German XQuAD 61.5 versus its English 79.5 on SQuAD 2.0). That transfer loss is the number to beat with
Danish training data (Section 5).

### 1.2 Generative decoders, passage given, by size

English, no fine-tuning on the target set:

| model | size | metric | value | source |
|---|---|---|---|---|
| Llama 3.2 1B (base) | 1.2B | SQuAD 1-shot EM | 49.2 | Llama 3.2 model card |
| Llama 3.2 3B (base) | 3.2B | SQuAD 1-shot EM | 67.7 | same |
| Llama 3.1 8B (base) | 8B | SQuAD 1-shot EM | 77.0 | Llama 3.1 model card |
| Llama 3 70B (base) | 70B | SQuAD 1-shot EM | 85.6 | same |
| Llama 3.1 405B (base) | 405B | SQuAD 1-shot EM | 89.3 | same |
| Llama 2 7B / 13B / 34B / 70B | | SQuAD 0-shot EM | 67.2 / 72.9 / 77.4 / 80.7 | arXiv 2307.09288, Table 23 |
| GPT-3 1.3B / 2.7B / 6.7B / 13B / 175B | | SQuAD 2.0 16-shot EM | 53.5 / 50.0 / 56.6 / 62.6 / 64.9 | arXiv 2005.14165, Table H.1 |
| Llama-2 7B, untuned, gold passage only, NQ-open | 7B | contains | 56.4 | arXiv 2401.14887, Table 1 |
| Llama-2 7B fine-tuned on SQuAD (Adapt-LLM), gold passage, SQuAD dev / NQ dev | 7B | accuracy as reported | 89.42 / 69.76 (versus 22.49 / 27.04 with Contriever-retrieved passages) | arXiv 2404.19705, Table 4 |
| LongChat-13B / MPT-30B-Instruct / GPT-3.5-Turbo / Claude-1.3, oracle passage, NQ-open | 13B / 30B / n.a. / n.a. | contains | 83.4 / 81.9 / 88.3 / 76.1 (closed-book 35.0 / 31.5 / 56.1 / 48.3) | arXiv 2307.03172, Table 1 |
| Llama-2 7B, gold plus proposition-level retrieval, NQ / TQA at 500-word budget | 7B | EM | 33.8 / 62.3 | arXiv 2312.06648, Table 5 |

Reading: untuned decoders cross 85 EM on SQuAD only at 70B. A 7B decoder crosses it after supervised
fine-tuning on SQuAD (89.4 with the gold passage). The 1 to 3B band sits at 49 to 68 EM one-shot in
English, which is exactly where our Danish oracle-intro numbers sit (39 to 70).

### 1.3 Danish, passage given: EuroEval MultiWikiQA-da and ScandiQA-da

Protocol: decoders 4-shot, 32 output tokens, prompt "Svar med maks. 3 ord", EM and F1 via the HF
squad_v2 metric (SQuAD normalisation); encoders fine-tuned on 1,024 training rows with early stopping on
256 validation rows, 10 seeds; test 2,048 rows. Board fetched 4 Sep 2026 (data stamp 30 Aug 2026).

| model | size | MultiWikiQA-da EM / F1 | ScandiQA-da EM / F1 | source |
|---|---|---|---|---|
| Llama-3.2-1B (base) | 1.2B | 37.62 / 52.21 | 46.59 / 51.92 | euroeval.com Danish board |
| gemma-3-1b-pt | 1.0B | 42.20 / 56.45 | 46.04 / 51.80 | same |
| gemma-3-1b-it | 1.0B | 0.00 / 17.01 (format failure) | 40.16 / 48.76 | same |
| DFM Mimir 1B (zero-shot on the board) | 1B | 66.25 / 79.94 | not run | same; Mimir report Table 9 gives 66.8 EM at 0-shot, 32 tokens |
| Qwen2.5-1.5B-Instruct | 1.5B | 53.17 / 68.86 | 47.88 / 54.62 | same |
| Qwen3-1.7B | 2.0B | 51.74 / 69.09 | 48.65 / 56.20 | same |
| gemma-2-2b | 2.6B | not run | 55.33 / 60.52 | same |
| Llama-3.2-3B-Instruct | 3.2B | 52.62 / 70.23 | 51.41 / 58.93 | same |
| Llama-3.2-3B (base) | 3.2B | not run | 56.85 / 62.25 | same |
| Qwen3-4B (thinking off) | 4.0B | 55.42 / 72.86 | 54.86 / 61.15 | same |
| gemma-3-4b-pt | 4.3B | 58.37 / 75.26 | 60.08 / 65.23 | same |
| gemma-3-4b-it | 4.3B | 46.06 / 70.94 | 39.59 / 56.17 | same |
| munin-7b-alpha | 7.2B | 60.05 / 74.94 | 58.57 / 63.89 | same |
| Llama-3.1-8B (base) | 8B | 61.69 / 78.62 | 61.02 / 66.47 | same |
| Llama-3.1-8B-Instruct | 8B | 53.92 / 74.43 | 48.80 / 59.47 | same |
| Llama-3.3-70B-Instruct | 70B | 41.74 / 70.18 | not run | same |
| Meta-Llama-3-70B (base) | 70B | not run | 63.62 / 69.67 | same |
| Ministral-3-14B-Base (board best EM) | 14B | 70.54 / 82.94 | | same |
| Olmo-3-1125-32B (board best F1) | 32B | 69.88 / 83.76 | | same |
| gpt-5.4 / gpt-5.5 | closed | 60.49 / 79.01 and 61.06 / 77.07 | | same |
| best fine-tuned encoder: AI-Sweden roberta-large-1160k | 355M | 33.77 / 40.23 | 47.30 / 52.99 | same |
| ltg/norbert3-large (best encoder on ScandiQA-da) | 354M | not run | 47.72 / 53.18 | results archive |
| FacebookAI/xlm-roberta-large | 561M | 25.71 / 32.87 | 42.69 / 48.46 | same |
| microsoft/mdeberta-v3-base | 278M | 13.24 / 18.30 | 32.69 / 38.47 | same |

MultiWikiQA paper (arXiv 2509.04111, Table 4, Danish row, F1 only, 2-shot): Mistral-Small-3.1-24B-Instruct
78.9, its base 77.1, Llama-3.1-8B-Instruct 75.2, Llama-3.1-8B 74.2, multilingual-e5-large fine-tuned 32.3,
XLM-RoBERTa-large fine-tuned 33.1. No human baseline exists for either Danish set; MultiWikiQA reports only
fluency ratings (156 respondents, mean above 2 of 3 stars in all 30 surveyed languages).

Three facts the Danish rows add. Size is not monotone under strict EM with 32-token answers: Llama-3.3-70B
scores 41.7 EM below Llama-3.2-1B's cousin gemma-3-1b-pt, because it writes sentences; its F1 of 70.2
shows the content is there. Danish pretraining beats size: Mimir 1B at 66.3 EM outreads Llama-3.1-8B at
61.7 and every closed model on the board. Instruction tuning costs EM under this protocol (gemma-3-4b
pt 58.4 versus it 46.1; Llama-3.1-8B base 61.7 versus instruct 53.9): the instruct models add words. The
board's best EM at any size is 70.5, which is where our 4B oracle-intro number already sits.

### 1.4 Human performance

| set | human EM / F1 | note | source |
|---|---|---|---|
| SQuAD 1.1 test | 82.3 / 91.2 (paper's first estimate 77.0 / 86.8) | second annotator scored against the others | arXiv 1606.05250, Table 5; arXiv 1810.04805, Table 2 |
| SQuAD 2.0 test | 86.9 / 89.5 | majority of about 4.8 crowdworkers | arXiv 1806.03822 |
| Natural Questions short answer | single annotator F1 57.5; 25-way super-annotator F1 75.7 | precision / recall 63.4 / 52.6 and 79.1 / 72.6 | Kwiatkowski et al. 2019, TACL Q19-1026, Table 3 |
| TriviaQA Wikipedia | 79.7 accuracy | one annotator, 986 questions | arXiv 1705.03551 |
| NorQuAD (Norwegian, human-written) | 78.13 / 91.14 | | arXiv 2305.01957 |
| Belebele English (multiple choice) | 97.6 percent | | arXiv 2308.16884 |

### 1.5 Answer to the size question

Passage-given EM exceeds 85 on entity questions in three published regimes: a fine-tuned encoder of 340M
or more with about 90k in-language examples (BERT-large 84.1, RoBERTa-large 88.9, DeBERTa-large 90.1); a
7B decoder fine-tuned on the same kind of data (Adapt-LLM 89.4); an untuned decoder at 70B (Llama 3 70B
85.6 one-shot) or 405B (89.3). Exceeding 90 EM is above human EM on every human-written set and is
reported only for DeBERTa-large on SQuAD 1.1 (90.1) and for models fine-tuned on the set's own training
split. For Danish, nothing published exceeds 70.5 EM under a passage-given protocol, but that ceiling is
protocol-made (4-shot, 32 tokens, verbatim spans), not a property of the language: our 3 to 4B readers hit
about 0.86 EM on DAISY when the answer is in the shown intro, matching the English 7B-fine-tuned band.

## 2. Danish and multilingual extractive readers we can run today

Searched 4 Sep 2026 on the Hugging Face Hub by pipeline, language tag, dataset tag and name. Finding: no
public model is fine-tuned on ScandiQA-da or MultiWikiQA-da. The alexandrainst, saattrupdan,
KennethEnevoldsen and danish-foundation-models organisations publish no question-answering head except
the two saattrupdan models below. Every model here fits a GTX 1060 6 GB in fp16 (largest 1.2 GB).

| model id | base, parameters, fp16 size | trained on | reported EM / F1 (which set) | use |
|---|---|---|---|---|
| saattrupdan/xlmr-base-texas-squad-da | XLM-R base, 277M, 0.55 GB | TExAS-SQuAD-da, machine-translated SQuAD (about 134k rows, 3 epochs) | 63.96 / 68.40 on the TExAS-da eval split | only Danish-trained reader with numbers |
| jacobshein/danish-bert-botxo-qa-squad | Danish BERT base, about 110M | translated SQuAD, 2 epochs | 30.37 / 37.15 on TExAS-da (per the saattrupdan card) | weak |
| saattrupdan/electra-small-qa-da | ELECTRA small, 13.7M | not reported | not reported | CPU-trivial, unknown quality |
| deepset/xlm-roberta-large-squad2 | XLM-R large, 560M, 1.12 GB | SQuAD 2.0 English | 79.46 / 83.79 SQuAD2; German XQuAD 61.51 / 78.80 | best zero-shot cross-lingual candidate |
| deepset/xlm-roberta-base-squad2 | XLM-R base, 277M | SQuAD 2.0 | 73.92 / 77.14; German XQuAD 48.74 / 62.55 | |
| timpal0l/mdeberta-v3-base-squad2 | mDeBERTa-v3 base, 278M | SQuAD 2.0 | 80.88 / 84.01 SQuAD2; no Danish number | most downloaded multilingual QA head |
| sjrhuschlee/mdeberta-v3-base-squad2 | mDeBERTa-v3 base, 278M | SQuAD 2.0 | 80.38 / 83.87 SQuAD2; SQuAD1 83.78 / 90.96 | alternative |
| alon-albalak/xlm-roberta-large-xquad | XLM-R large, 559M | XQuAD (11 languages, no Danish) | 87.13 / 94.78 on held-out XQuAD | trained on the eval family, optimistic |

Base encoders to fine-tune ourselves (no QA head shipped): FacebookAI/xlm-roberta-large 561M,
danish-foundation-models/encoder-large-v1 355M, AI-Sweden-Models/roberta-large-1160k 355M, ltg/norbert3-large
354M, NbAiLab/nb-bert-large 356M, jhu-clsp/mmBERT-base 308M, microsoft/mdeberta-v3-base 278M,
vesteinn/DanskBERT 125M, jonfd/electra-small-nordic 22M.

Datasets: alexandrainst/scandi-qa Danish 7,810 rows (MKQA questions, NQ contexts DeepL-translated,
answerable-only subset used by EuroEval; card splits 6,311 / 749 / 750); alexandrainst/multi-wiki-qa
Danish 5,000 rows (Gemini-1.5-pro generated from the 20231101 Danish Wikipedia dump, answers verbatim,
questions rephrased to hinder word matching); TExAS-SQuAD-da (translated SQuAD, no public dataset card
found, model exists); NorQuAD 4,752 human-written Norwegian pairs.

What the encoder rows say about data size. The EuroEval encoder scores (best 33.8 EM on MultiWikiQA-da,
47.7 on ScandiQA-da) are 1,024-example numbers. With 3,800 human-written examples (NorQuAD) NB-BERT-large
reaches 69.68 EM / 81.27 F1 and XLM-R 64.52 / 78.42 (arXiv 2305.01957, Table 4); with 134k translated
examples XLM-R base reaches 63.96 EM on translated SQuAD. So a 300 to 560M encoder trained on the union
of ScandiQA-da, MultiWikiQA-da and TExAS-da (about 145k rows, roughly one GPU-hour per epoch on the 1060)
should read Danish Wikipedia at 65 to 75 EM on its own test sets, which is the same band as our untuned
3 to 4B decoders on DAISY intros, at 20 to 50 times lower cost per question and with spans that are
verbatim by construction.

## 3. Retrieve, rerank, read

### 3.1 Retrieval recall as a function of k (English, Wikipedia, 100-word passages)

| retriever | top-1 | top-5 | top-10 | top-20 | top-100 | source |
|---|---|---|---|---|---|---|
| BM25, NQ dev | 22.3 | 43.8 | | 62.3 | 76.0 | arXiv 2204.07496, Table 4 |
| BM25, NQ test | | | | 59.1 | 73.7 | arXiv 2004.04906, Table 2 |
| DPR single, NQ test | 44.6 to 46.0 | 67.8 to 68.1 | 74.5 | 79.5 | 86.8 | arXiv 2502.02464, Table 4; arXiv 2109.08133, Table 1 |
| BGE, NQ test | 48.0 | 72.2 | 78.5 | 82.7 | 89.5 | arXiv 2502.02464, Table 4 |
| RocketQA, NQ | | 74.0 | | 82.7 | 88.5 | arXiv 2010.08191, Table 2 |
| DPR, TriviaQA test | 54.6 | 70.8 | | 79.5 | 85.0 | arXiv 2109.08133; arXiv 2004.04906 |
| BM25 top-1000 reranked by monoT5-3B, NQ dev | 44.2 | 68.3 | | 78.7 | 83.7 | arXiv 2204.07496, Table 4 |

Reading: the first passage is right less than half the time even for trained dense retrievers; the fifth
raises recall by 20 to 25 points; the twentieth by another 10. A cross-encoder rerank of a lexical top-1000
doubles top-1 (22.3 to 44.2) and matches a trained dense retriever at every k. Our subject-name query on
the Danish Wikipedia search API gives answer recall@3 of 78.7 percent at intro granularity, which is
already above DPR top-20 on NQ; the missing 21 percent are pages whose introduction does not contain the
answer, not missing pages.

### 3.2 How much a reranker buys the reader

| system | without rerank | with rerank | gain | source |
|---|---|---|---|---|
| Re2G, KILT NQ accuracy / R-precision (BART reader) | 45.22 / 63.71 | 51.73 / 70.78 | +6.5 / +7.1 | arXiv 2207.06300, Table 1 |
| Re2G, KILT TriviaQA accuracy | 60.99 | 76.27 | +15.3 | same |
| RankRAG-8B ablation: NQ / TriviaQA / PopQA EM | 48.0 / 80.3 / 49.3 | 50.6 / 82.9 / 57.6 | +2.6 / +2.6 / +8.3 | arXiv 2407.02485, Table 3 |
| R2-D2, generative reader, TriviaQA EM | 65.38 | 69.14 | +3.8 | arXiv 2109.03502, Table 3 |
| UPR-reranked top-1000 then FiD, SQuAD-open test / TriviaQA test EM | 45.8 / 68.5 | 54.0 / 71.2 | +8.2 / +2.7 | arXiv 2204.07496, Table 7 |
| Qwen2.5-7B-Instruct agentic RAG on HotpotQA, EM, cross-encoder top-20 to top-5 | 51.5 (no reranker) | 53.2 | +1.7 | arXiv 2606.21553, Table 2 |
| RankRAG text: reranking N=20 to 100 candidates | | | +5.9 to +9.1 EM across three tasks | arXiv 2407.02485, Figure 5 |

Reading: rerankers add 2 to 8 EM points to the reader when the candidate pool is wide (20 to 1000) and the
reader sees a handful. The gain is largest on long-tail entity sets (PopQA +8.3), which is DAISY's regime.

### 3.3 How many passages, and how long, for a small untuned reader

| finding | numbers | source |
|---|---|---|
| Trained fusion readers want many passages | FiD-base NQ dev EM at 5 / 10 / 25 / 50 / 100 passages: 37.8 / 42.3 / 45.3 / 45.7 / 46.5; FiD-KD: top-10 by DPR 42.9 versus top-100 48.2 | arXiv 2007.01282, Table 2; arXiv 2012.04584, Sec. 3.2 |
| Untuned 7B readers lose to distractors fast | Llama-2 7B NQ-open contains: gold only 56.4; gold plus 1 / 2 / 4 / 10 retrieved distractors (far position) 45.9 / 34.6 / 27.5 / 25.4; gold plus 1 to 8 random documents 48.6 to 58.4 (no loss) | arXiv 2401.14887, Tables 1 and 2 |
| 13 to 30B readers below closed-book at 20 to 30 documents | GPT-3.5-Turbo closed-book 56.1; gold at middle positions of 20 documents 53.8; of 30 documents 50.5 | arXiv 2307.03172, Tables 1, 6, 7 |
| Frontier long-context: k of 5 to 10 captures most of the gain | Gemini-1.5-Pro RAG accuracy at k = 1 / 5 / 10 / 50 / 100: 20.2 / 37.9 / 41.2 / 44.1 / 44.1 | arXiv 2407.16833, Table 7 |
| Smaller retrieval units help a 7B reader at a fixed word budget | Llama-2 7B EM, GTR retrieval, 100 / 500 words: passages NQ 30.0 / 33.9, propositions 32.1 / 33.8; TQA passages 56.9 / 60.0, propositions 58.8 / 62.3 | arXiv 2312.06648, Table 5 |
| Chunk size 256 to 512 tokens best; 2048 worst | faithfulness / relevancy at 128 / 256 / 512 / 1024 / 2048 tokens: 95.7 / 97.2 / 97.6 / 94.3 / 80.4 and 97.2 / 97.8 / 97.4 / 95.6 / 91.1 | arXiv 2407.01219, Table 3 |
| Same total length, fewer documents is better | up to 10 to 20 percent drop when 20 documents replace 8 at fixed 2,400 tokens (Llama 3.2 3B, Qwen2.5 7B, Gemma2 9B, GPT-4o-mini) | arXiv 2503.04388 |
| 8B reader peaks at 16k context then declines with 128-token chunks | Llama3.1-8B EN.QA best at 16k tokens, 70B at 48k | arXiv 2409.01666 |
| Our own readers on 3 intros | EM given answer present 0.73 Gemma 4B, 0.67 Llama 3B, 0.64 Qwen 3B, 0.59 Mimir, 0.37 Llama 1B; distraction rate (EM when absent) 0.006 to 0.045 | RESULTS.md reading fidelity |

Recommendation for a 1 to 4B untuned reader: sections of 100 to 250 words (one to two Wikipedia
paragraphs), a wide candidate pool (every section of the top-3 pages, 20 to 60 candidates), a
cross-encoder rerank, and only the top 3 to 5 sections in the prompt, best first. Never 20 intros. The
untuned-reader curves above say the third distractor costs more than the third relevant passage gains.

### 3.4 Embedders and rerankers that fit 6 GB, with Danish numbers

Scandinavian Embedding Benchmark (SEB, arXiv 2406.02396) Danish retrieval tasks, nDCG@10 from the SEB
result cache (DanFEVER is Wikipedia-evidence retrieval and saturates near 40 for every model because
recall@100 is only 48, so Twitterhjerne and TV2Nord separate models better):

| model | parameters, fp16 | DanFEVER | TV2Nord | Twitterhjerne | SEB Danish average (paper Table 2) | MIRACL nDCG@10 (own paper) |
|---|---|---|---|---|---|---|
| intfloat/multilingual-e5-small | 118M, 0.24 GB | 38.3 | 90.4 | 57.4 | 58.9 | 60.8 |
| intfloat/multilingual-e5-base | 278M, 0.56 GB | 40.1 | 92.7 | 65.4 | 60.9 | 62.3 |
| intfloat/multilingual-e5-large | 560M, 1.12 GB | 40.5 | 95.4 | 74.4 | 63.1 | 66.5 |
| intfloat/multilingual-e5-large-instruct | 560M | 39.5 | 93.7 | 77.2 | | 65.7 |
| BAAI/bge-m3 dense | 568M, 1.14 GB | 38.2 | 92.6 | 62.1 | | 69.2 (71.5 dense plus sparse plus multi-vector) |
| jinaai/jina-embeddings-v3 | 572M, 1.14 GB | 40.3 | 94.2 | 73.2 | | |
| Alibaba-NLP/gte-multilingual-base | 305M, 0.61 GB | | 94.1 | | | 62.1 |
| Snowflake/snowflake-arctic-embed-l-v2.0 | 568M | 40.3 | 94.0 | 75.3 | | |
| paraphrase-multilingual-MiniLM-L12-v2 | 118M | 36.5 | 73.3 | 51.2 | 52.7 | |
| KennethEnevoldsen/dfm-sentence-encoder-large | 407M | 36.9 | 80.8 | 17.0 | | |

Rerankers (cross-encoders; no Danish number published by anyone; MIRACL has no Danish, MKQA has Danish
but only averages are reported):

| model | parameters, fp16 | documented gain | source |
|---|---|---|---|
| BAAI/bge-reranker-v2-m3 | 568M, 1.14 GB | MIRACL nDCG@10 average: bge-m3 dense 67.91 to 72.84 reranked (+4.9); MKQA nDCG@10 54.17; BEIR 53.65 | model card result table; jina card table |
| Alibaba-NLP/gte-multilingual-reranker-base | 306M, 0.61 GB | MIRACL 62.1 to 68.5 (+6.4); MKQA R@20 65.8 to 67.2; BEIR 51.1 to 55.4 | arXiv 2407.19669, Table 5 |
| jinaai/jina-reranker-v2-base-multilingual | 278M, 0.56 GB | MKQA nDCG@10 54.83; BEIR 53.17; MLDR R@10 68.95 | model card |
| cross-encoder/mmarco-mMiniLMv2-L12-H384-v1 | 118M, 0.24 GB | mMARCO MRR@10 English 0.366 (BM25 0.184), German 0.278; MKQA 53.37 | arXiv 2108.13897; jina card |
| unicamp-dl/mt5-base-mmarco-v2 (monoT5 multilingual) | 582M, 1.16 GB | Mr.TyDi MRR@100 0.551 versus BM25 0.313; Recall@100 0.835 versus 0.720 | arXiv 2108.13897, Table 4 |
| BAAI/bge-reranker-base | 278M | Chinese and English only; no multilingual number | model card |

Practical: on the 1060, a 4B reader at Q4 (about 2.7 GB) plus bge-reranker-v2-m3 in fp16 (1.14 GB) fit
together; an 8B reader at Q4 (4.4 to 4.9 GB) leaves room only for the 118M MiniLM reranker or a CPU
reranker. Reranking 40 sections of 200 words with a 278M cross-encoder costs about 0.3 to 0.6 s on the
1060 and 3 to 6 s on CPU.

## 4. Query and page finding

### 4.1 Page-level retrieval and entity linking on Wikipedia

| method | task | number | source |
|---|---|---|---|
| tf-idf | KILT NQ / TriviaQA page-level R-precision | 28.1 / 46.4 | arXiv 2009.02252, Table 4 |
| BM25 | KILT NQ / TriviaQA page-level R-precision (validation) | 25.8 / 29.4 | arXiv 2101.00117, Table 3 |
| DPR (trained on NQ) | same | 54.3 / 44.5 | arXiv 2009.02252, Table 4 |
| Multi-task DPR | same | 59.4 / 61.5 | same |
| RAG | same | 59.5 / 48.7 | same |
| BLINK entity linker plus flair NER | same | 24.5 / 65.6 | same |
| GENRE (generate the title with a title trie) | same | 60.3 / 69.2 | arXiv 2010.00904, Table 3 |
| GENRE, entity disambiguation AIDA micro-F1 | | 93.3 (BLINK 79.6 without candidate set) | same, Table 1 |
| BLINK bi-encoder over full Wikipedia, unseen mentions | recall@1 / @10 / @100 | 71.5 / 92.7 / 96.7 | arXiv 1911.03814, Table 7 |
| alias table (anchor-text prior) | TAC-KBP 2010 recall@100 | 89.5 (extended 91.7; BM25 68.9) | same, Table 5 |
| mGENRE, Danish held-out Wikipedia hyperlinks (1,000 per language) | accuracy | alias table 90.6; mGENRE 95.5 | arXiv 2103.12528, Appendix Table 11 |
| exact title keyword match | FEVER document recall at k = 5 | 88.86 (plus page views 91.98; tf-idf baseline 70.20) | arXiv 1811.07039, Table 2 |
| MediaWiki title search with noun phrases | FEVER document recall at 3 / 5 / 7 results | 92.60 / 93.30 / 93.55 | arXiv 1809.01479, Table 1 |
| ReAct search[entity] on Wikipedia (first 5 sentences) | HotpotQA EM, PaLM-540B | 27.4 (CoT 29.4); with PaLM-8B and 62B, prompted ReAct is the worst of four methods | arXiv 2210.03629, Table 1, Figure 3 |
| our model-written queries | first hit is the subject page | 0.48 to 0.57; empty results 20 to 26 percent | RESULTS.md |

Reading: when the question names its entity (as most DAISY questions do: a work, a person, a building),
title matching against Wikipedia titles, redirects and anchor aliases finds the page about 89 to 93 percent
of the time on FEVER and 90 to 96 percent of the time for Danish hyperlink mentions. Trained page
retrievers on question-shaped queries reach only 54 to 60 percent on NQ. Our model queries land on the
subject page about half the time, so the largest documented headroom in the whole pipeline is here: from
about 0.5 to about 0.9 by matching a capitalised or quoted span of the question against page titles and
redirects, with the search API and the English Wikipedia as fallbacks (da.wikipedia has 315,756 articles
and 989,080 pages including redirects as of 4 Sep 2026; en.wikipedia 7,235,479 articles).

### 4.2 Query rewriting: what the gain is and what size it needs

| method | reader / retriever | without | with | gain | source |
|---|---|---|---|---|---|
| Rewrite-Retrieve-Read, LLM rewriter (ChatGPT), Bing | ChatGPT reader, HotpotQA / AmbigNQ / PopQA EM | retrieve-then-read 30.47 / 45.80 / 43.20 | 32.80 / 46.40 / 46.00 | +2.3 / +0.6 / +2.8 | arXiv 2305.14283, Table 2 |
| same, trainable T5-large rewriter (RL) | same | same | 34.38 / 47.80 / 45.72 | +3.9 / +2.0 / +2.5 | same |
| same, Vicuna-13B reader, MMLU accuracy | | retrieve-then-read 40.2 | LLM rewriter 42.0; trained 43.2 | +1.8 / +3.0 | same, Table 3 |
| HyDE with generator size | Contriever, TREC DL19 / DL20 nDCG@10 | 44.5 / 42.1 | Flan-T5-XXL 11B 48.9 / 52.9; Cohere 52B 53.8 / 53.8; GPT 175B 61.3 / 57.9 | +4.4 to +16.8 | arXiv 2212.10496, Table 4 |
| HyDE multilingual, Mr.TyDi MRR@100 | mContriever | sw 38.3, ko 22.3, ja 19.5, bn 35.3 | 41.7, 30.6, 30.7, 41.3 | +3 to +11 with a 175B generator | same, Table 3 |
| Query2doc by generator size | BM25, DL19 / DL20 nDCG@10 | 51.2 / 47.7 | babbage 1.3B 52.0 / 50.2; curie 6.7B 55.1 / 50.1; davinci-003 66.2 / 62.9 | +0.8 to +15 | arXiv 2303.07678, Table 3 |
| Query expansion by Flan-T5 size | BM25 MS MARCO | | "Q2D requires at least an 11B parameter model to reach parity with the BM25+Bo1 baseline; the CoT approach only needs a 3B model" | | arXiv 2305.03653, Figure 2 |
| Expansion versus retriever strength | DL19 nDCG@10 | DPR 38.4, ContrieverFT 62.3, MonoT5-3B 71.7 | with HyDE plus Doc2Query +21.9, +9.0, minus 4.5 | helps weak retrievers, hurts strong ones | arXiv 2309.08541, Table 1 |
| RaFe, Qwen-7B rewriter | Qwen-max reader, FreshQA / NQ | 62.56 / 51.50 | SFT rewriter 63.27 / 51.94; RaFe 64.85 / 52.86 | +1 to +2 | arXiv 2405.14431 |
| Search-R1, Qwen2.5-3B-Base, E5 top-3 | NQ / TriviaQA / PopQA EM | RAG 34.8 / 54.4 / 38.7; IRCoT 11.1 / 31.2 / 20.0; SFT 24.9 / 29.2 / 10.4 | RL-trained 40.6 / 58.7 / 43.5 | +5.8 / +4.3 / +4.8 over RAG | arXiv 2503.09516, Table 2 |
| Search-R1, Qwen2.5-7B | same | RAG 34.9 / 58.5 / 39.2 | 48.0 / 63.8 / 45.7 | +13.1 / +5.3 / +6.5 | same |

Reading: prompted query rewriting with a small model is worth 1 to 3 EM points; generation-based
expansion (HyDE, Query2doc) needs an 11B-plus generator to help a lexical retriever and hurts a strong
retriever; a trained rewriter or RL search policy on a 3B is worth 5 to 6 points on single-hop sets, and
multi-step prompting (IRCoT, ReAct) below 8B is worse than one retrieval call. Our own agentic result
(40.0 EM untrained 3 to 4B, equal to Search-R1's trained 3B on PopQA at 43.5 contains) is consistent.
Entity-title matching (Section 4.1) has three to ten times the headroom of rewriting for a benchmark
whose questions name their subject.

## 5. Fine-tuning the reader on public Danish data: is it cheating?

### 5.1 The rule as the field states it

The benchmark authors' own protocol trains on the train split: "The few-shot examples come from the
training split. The encoder models were trained on the training split, with early stopping based on the
validation split, and the final performance reported on the test split" (MultiWikiQA, arXiv 2509.04111).
EuroEval's methodology page: "the few-shot examples come from the training data of the task", and it
argues few-shot and fine-tuning are "comparable" evaluation methodologies (citing arXiv 2309.05858).
Sainz et al. (arXiv 2310.18018) define contamination as "any breach in the strict control of datasets
required by the experimental protocol" and grade it: "When the evaluation split is involved, the
experiment is completely invalidated. This is the most harmful level of contamination", whereas "When the
train or development splits are involved, this would not affect comparisons with other models that have
been developed using those same splits, but it does invalidate conclusions claiming zero-shot or few-shot
performance". Dodge et al. (arXiv 2104.08758): "If task labels are available in the pretraining corpus, a
valid train-test split is not made and the test set is not suitable for evaluating the model's
performance". Xu et al. (arXiv 2406.04244) define benchmark data contamination as exposure "to benchmark
data during the training process" and do not treat labelled train splits as contamination.

Applied to DAISY:

| action | verdict | why |
|---|---|---|
| fine-tune on ScandiQA-da train, MultiWikiQA-da, TExAS-da, NorQuAD, SQuAD | fair; standard; must be stated in the model card and the label "zero-shot" must be dropped | public train splits of other datasets |
| fine-tune, tune prompts, or pick few-shot examples from any DAISY row | cheating | test-split exposure (Sainz level 1) |
| restrict retrieval to the canon list, or use the subject or page fields | cheating | hidden benchmark fields and a benchmark-specific prior; the deployed system could not do it |
| try 30 pipeline variants on the 592 and report the best | test-set overfitting, the quiet version of cheating | no held-out split; the fix is a fixed dev half (296 rows) or MultiWikiQA-da as the development set, and reporting how many variants were tried |
| report EuroEval MultiWikiQA-da after training on the full 5,000 alexandrainst rows | cheating for that board (its 2,048 test rows are sampled from those 5,000); fair for DAISY | train on EuroEval's 1,024 train rows only when that board is the target |
| pretraining on Danish Wikipedia (Mimir, Munin) | fair, and the group's own method | corpus, not benchmark |

### 5.2 What fine-tuning buys, by evidence

| evidence | numbers | source |
|---|---|---|
| Encoder gain with training set size (Danish and Norwegian) | 1,024 rows: 33.8 EM MultiWikiQA-da, 47.7 ScandiQA-da; 3,800 human rows: NB-BERT 69.7 EM NorQuAD; 134k translated rows: XLM-R base 64.0 EM TExAS-da | EuroEval; arXiv 2305.01957, Table 4; saattrupdan card |
| Cross-lingual transfer loss without in-language data | XLM-R large: 79.5 EM English SQuAD 2.0, 61.5 German XQuAD, 49.4 German MLQA | deepset card |
| Decoder LoRA on SQuAD 2.0 (non-peer-reviewed GitHub) | Llama-3-8B-Instruct 51.85 EM before, 80.13 after 3 epochs; Llama-2-7B-chat 18.76 before, 47.22 after 1.2 epochs, 73.11 after 8 epochs; DeBERTa-v3-large 80.01 on the same split | github.com/teticio/llama-squad |
| Decoder fine-tuned on SQuAD then given the gold passage | Llama-2 7B 89.42 on SQuAD dev, 69.76 on NQ dev | arXiv 2404.19705, Table 4 |
| SFT can hurt a 3B when the training format mismatches inference | Qwen2.5-3B SFT 24.9 NQ EM versus untrained RAG 34.8 | arXiv 2503.09516, Table 2 |
| Encoder LoRA equals full fine-tuning at 0.3 percent of parameters | DeBERTaV3-base SQuAD 1.1 full 86.0 / 92.7, LoRA 86.4 to 86.7 EM; SQuAD 2.0 full 85.4 / 88.4, LoRA 83.6 to 85.0 | arXiv 2303.10512, Table 2 |
| Extractive versus generative readers at equal retrieval | NQ / TriviaQA EM: ELECTRA-large extractive (440M) 51.8 / 68.9, T5-large generative (880M) 52.3 / 68.6, hybrid 54.7 / 70.5 | arXiv 2101.00178, Table 2 |
| same, R2-D2 | extractive 50.8 / 65.0, generative 49.9 / 65.4, combined 55.0 / 69.9 | arXiv 2109.03502, Table 2 |
| extractive readers generalise better out of domain and on rare answers; generative better on passages over 600 words | MRQA out-of-domain F1: T5 extractive 64.49, T5 generative 61.82 | arXiv 2203.07522, Table 4 |

Estimate for DAISY, reading only (the retrieval factors do not move). The oracle condition's lenient-minus-
strict gap is the part a few hundred LoRA steps on MultiWikiQA-da plus ScandiQA-da will almost surely
close, because that data teaches "answer with the span, nothing else" in Danish: about 4 points for Gemma
4B, Qwen 3B and Mimir, 7 for Llama 3B, 19 for Llama 1B. Extraction gains beyond format are smaller for the
3 to 4B models, which already read at 0.86 given presence, so the honest range is +3 to +8 EM for the 3 to
4B readers and +10 to +18 for Llama 1B, with the Search-R1 warning that the inference prompt must be the
training prompt. For a 300 to 560M encoder trained on the 145k-row union, expect 65 to 75 EM on its own
held-out Danish sets and about the same as the untuned 4B decoders on DAISY intros, plus two properties
the decoders lack: verbatim spans and a calibrated span score usable for selective prediction.

## 6. Verdict

### 6.1 Three paths, expected EM on the 592, cost, and the sceptic's line

Assumptions: page finding raised from about 0.5 to 0.85 to 0.9 by title and alias matching with search
and English-Wikipedia fallback (Section 4.1); answer coverage raised from 0.787 (intros) to 0.92 to 0.95 by
sectioning the found pages and reranking 20 to 60 sections to the top 3 to 5 (Sections 3.1 to 3.3); reader
EM given presence 0.86 (untuned 4B), 0.88 to 0.90 (untuned 8B, from the MultiWikiQA-da and SQuAD size
curves), 0.90 (fine-tuned 4B or 8B), 0.80 to 0.88 (fine-tuned encoder, from NorQuAD and TExAS). Product
ranges are rounded to 5.

| path | pipeline | expected EM | cost per question on the 1060 | what the sceptical professor says |
|---|---|---|---|---|
| (a) reader at most 4B, untuned | title match plus search union; full page sectioned to 150 to 250 words; bge-reranker-v2-m3 or jina-reranker-v2 top-3; typed answer post-processing | 60 to 70 (0.87 times 0.93 times 0.86 is 0.70; 0.85 times 0.92 times 0.82 is 0.64) | 4 to 7 s; 2 to 4 HTTP calls; about 1.5k prompt tokens | "The gain is retrieval engineering, not the model; show the ablation per stage and the dev/test split you tuned on." Answer: yes, that is the finding, and the stages are generic Wikipedia QA components, none canon-specific |
| (a') as (a) plus a few hundred LoRA steps on MultiWikiQA-da and ScandiQA-da | same | 65 to 75 | same plus one GPU-hour of training | "No longer zero-shot; report it as fine-tuned on public Danish RC, like every EuroEval encoder row." Fair when stated |
| (b) 7 to 8B reader at four bits (Llama-3.1-8B Q4_K_M 4.92 GB, Qwen2.5-7B Q4_K_M 4.68 GB, Mistral-7B-v0.3 Q4_K_M 4.37 GB) | same pipeline; reranker on CPU or the 118M MiniLM on GPU; 4k context (KV cache about 0.5 GB for Llama 8B) | 70 to 80 untuned (0.90 times 0.95 times 0.89 is 0.76); 75 to 82 with LoRA | 10 to 20 s (about 2 to 3 tokens per second of output on a 1060 at Q4; prompt processing dominates); 5 GB VRAM, no room for a GPU reranker above 118M | "Now you have changed the model class; the record is 'small model plus tool beats 70B closed book', an 8B is still 9 times smaller, but say so." Also: MultiWikiQA-da shows 8B base beats 8B instruct by 8 EM, so use a base model with few-shot or the fine-tuned variant |
| (c) extractive encoder reader | title match plus search union; sections; XLM-R-large or dfm encoder-large-v1 fine-tuned on the 145k-row Danish union, span score used to pick the best section directly (reader as reranker, as in DPR and R2-D2); typed post-processing | 55 to 70 (0.87 times 0.93 times 0.80 is 0.65); higher if the answers are verbatim in the page, lower on year and number questions that need normalisation | 0.1 to 0.3 s; the whole system is CPU-feasible; 1.2 GB VRAM | "This is 2020 technology and it needs a training set; but it is 30 times cheaper and it cannot hallucinate a span that is not on the page." Also the fairness objection is the same as (a') and the answer is the same |
| (c') hybrid: encoder locates the span, 4B decoder normalises the type | (c) plus one short decoder call with the span and the question | 65 to 75; UnitedQA and R2-D2 report +2 to +5 EM for extractive plus generative over either alone | 2 to 4 s | "Two models, more moving parts; justify the second with the ablation" |

Above 90: not credible on this benchmark by any of these paths. It requires every stage above 0.965, a
reader EM above the SQuAD-human EM (82 to 87), and a passage coverage no Wikipedia system has published.
The published end-to-end ceilings with trained retrievers and readers are 64 EM on NQ and 78 to 85 on
TriviaQA (Atlas 11B), and the best passage-given Danish EM at any size is 70.5. A number above 90 on DAISY
would itself be evidence of a benchmark-specific prior, and a sceptical reader would look for one. The
target to set is 80 with (b) or (a'), 85 as a stretch with (b) plus LoRA and the hybrid extractor.

### 6.2 Is it possible without a bigger model?

Yes for 70 to 75, and the reason is in Section 0: the 3 to 4B readers already read at 0.86 given presence,
and Mimir 1B reads Danish at 0.70 on the oracle intros and 66.3 EM on MultiWikiQA-da, above Llama-3.1-8B.
The missing 30 points are page finding and coverage, which are retrieval engineering with generic
components (title and alias matching, sectioning, a 300M cross-encoder). A bigger reader adds 3 to 6
points of reading (Llama 3.2 3B to 3.1 8B: +9 on English SQuAD one-shot, +9 on MultiWikiQA-da base to
base) and better queries, which is why (b) is the path to 80. The simplest elegant method, in one line:
find the page by its title, show the reader the three best sections of that page instead of its
introduction, and make the reader answer in the type the question asks for.

### 6.3 The "same terms" argument: which comparisons stay fair

| comparison | fair? | condition |
|---|---|---|
| our small model plus Danish Wikipedia lookup versus the paper's 70B closed-book 22.5 on the same 592, same prompt, same scorer | fair as a capability-per-cost statement, provided it is labelled "with tool" versus "without tool" and the cost line (seconds, tokens, calls, VRAM) is printed next to it | the paper's condition is closed-book by design; the comparison shows what one lookup buys, not that a 4B knows more than a 70B |
| same, described as "beats the 70B" without the tool label | not fair | it hides the condition change |
| our system versus a 70B plus the same lookup | the comparison a sceptic will ask for; we cannot run it on the 1060 | the MultiWikiQA-da board gives the direction: Llama-3.3-70B reads Danish passages at 41.7 EM under a strict short-answer protocol, below Mimir 1B's 66.3, so a 70B plus lookup is not guaranteed to win under strict EM; under F1 it would |
| fine-tuned on public Danish RC train splits versus untuned models | fair if declared; the number is no longer zero-shot | Sainz et al. level 2; EuroEval does exactly this for encoders |
| retrieval over all of da.wikipedia (315,756 articles) plus en.wikipedia versus retrieval over the canon pages | only the former is fair | the canon list is a benchmark-specific prior; the same system must work for a question about any Danish topic |
| tuned on a fixed dev half, reported on the other half, then on all 592 with the variant count | fair | prevents test-set overfitting on a 592-row set where one standard error is 1.2 points |
| EuroEval MultiWikiQA-da via their CLI for Gemma 3 4B and Qwen 2.5 3B (board holes) | identical terms by construction | do not train on the 5,000-row pool first |
| PopQA long-tail with Self-RAG's released passages, untrained 4B versus untrained 7B and 13B rows | identical terms by construction | contains-gold metric, 1,399 rows |

## 7. Sources

Reader ceilings: BERT arXiv 1810.04805; RoBERTa 1907.11692; DeBERTa 2006.03654; DeBERTa-v3 2111.09543;
XLM-R 1911.02116; SQuAD 1606.05250 and 1806.03822; Natural Questions TACL Q19-1026; TriviaQA 1705.03551;
Llama 2 2307.09288 (Tables 22, 23); Llama 3.2 and 3.1 model cards (huggingface.co/meta-llama); GPT-3
2005.14165 (Table H.1); Gemma 3 2503.19786 (Table 9); Lost in the Middle 2307.03172; The Power of Noise
2401.14887; Adapt-LLM 2404.19705; Dense X Retrieval 2312.06648; MultiWikiQA 2509.04111; ScandEval
2304.00906; Encoder vs Decoder 2406.13469; NorQuAD 2305.01957; Belebele 2308.16884; EuroEval Danish
leaderboard (euroeval.com/leaderboards/Monolingual/danish, CSV in github.com/EuroEval/leaderboards,
raw results.tar.gz); Mimir report Table 9 (lit/GROUP-PAPERS.md).

Models: huggingface.co/saattrupdan/xlmr-base-texas-squad-da; deepset/xlm-roberta-large-squad2;
deepset/xlm-roberta-base-squad2; timpal0l/mdeberta-v3-base-squad2; sjrhuschlee/mdeberta-v3-base-squad2;
deepset/deberta-v3-large-squad2; alon-albalak/xlm-roberta-large-xquad; jacobshein/danish-bert-botxo-qa-squad;
saattrupdan/electra-small-qa-da; datasets alexandrainst/scandi-qa and alexandrainst/multi-wiki-qa; GGUF sizes
from bartowski repositories (HF API, 4 Sep 2026).

Retrieval and reranking: DPR 2004.04906; RocketQA 2010.08191; DensePhrases retrieval 2109.08133; Rankify
2502.02464; UPR 2204.07496; FiD 2007.01282; FiD-KD 2012.04584; Atlas 2208.03299; Re2G 2207.06300; R2-D2
2109.03502; UnitedQA 2101.00178; BERT reranker 1901.04085; monoT5 2003.06713; BGE M3 2402.03216; mGTE
2407.19669; mMARCO 2108.13897; ColBERTv2 2112.01488; RankRAG 2407.02485; Best practices in RAG
2407.01219; RAG vs long context 2407.16833; More documents same length 2503.04388; OP-RAG 2409.01666;
Semantic chunking 2410.13070; Agentic RAG dissection 2606.21553; SEB 2406.02396 and the SEB result cache
(github.com/KennethEnevoldsen/scandinavian-embedding-benchmark); mE5 2402.05672; Choose Your QA Model
Wisely 2203.07522.

Page finding and query rewriting: KILT 2009.02252; multi-task KILT retrieval 2101.00117; GENRE 2010.00904;
mGENRE 2103.12528; BLINK 1911.03814; EntQA 2110.02369; FEVER title matching 1811.07039 and 1809.01479;
ReAct 2210.03629; Rewrite-Retrieve-Read 2305.14283; HyDE 2212.10496; Query2doc 2303.07678; Jagerman et al.
2305.03653; Weller et al. 2309.08541; RaFe 2405.14431; Self-RAG 2310.11511; CRAG 2401.15884; RQ-RAG
2404.00610; Search-R1 2503.09516; R1-Searcher 2503.05592; ReSearch 2503.19470; IRCoT 2212.10509.

Hygiene and fine-tuning: Sainz et al. 2310.18018; Dodge et al. 2104.08758; Magar and Schwartz 2203.08242;
Xu et al. 2406.04244; EuroEval methodology and FAQ pages (github.com/EuroEval/EuroEval); AdaLoRA
2303.10512; github.com/teticio/llama-squad (non-peer-reviewed); Wikipedia statistics from the MediaWiki
siteinfo API, 4 Sep 2026.

Numbers the sources do not give (asked for, not found): FiD and DPR per-k curves as values (figures only);
Lost in the Middle GPT-4 oracle; bge-reranker-v2-m3 MIRACL numbers as text from BAAI (chart images only,
the +4.9 comes from the FlagEmbedding result table); any Danish reranking or Danish HyDE result; any
peer-reviewed LoRA-on-SQuAD table for Llama, Qwen or Gemma; any human EM on ScandiQA or MultiWikiQA.
