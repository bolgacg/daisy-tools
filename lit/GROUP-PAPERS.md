# The Odense NLP group on paper: what they measured, how, and which of their numbers we can match

Literature sweep for the daisy-tools study (job 4203, Schneider-Kamp group, SDU IMADA / Danish Foundation Models).
Swept 4 Sep 2026: arXiv author searches (Schneider-Kamp, Galke, Barmina, Beltoft, Mellgren, From), dblp records
(pid 36/5338 and 200/7830), GitHub orgs schneiderkamplab, lgalke, danish-foundation-models, aisilab, Hugging Face
danish-foundation-models and schneiderkamplab, foundationmodels.dk, the EuroEval source and leaderboards repo, and
the llama.cpp PR we run Mimir on. portal.findresearcher.sdu.dk returned 403 and was not used. Every number below
carries the table or section it came from; "not found" means I looked and it is not published.

Reading order if you have ten minutes: Section 0, then Section 3.2 (why our Mimir 5.6 is not their 9.6), then the
hidden-apples table in Section 2, then the ranked ideas in Section 4.

---

## 0. The five facts that matter for our study

1. **Their Daisy number was almost certainly computed on the same 592 rows we use, not on 741.** The Mimir report's
   Table 11 lists the dataset as `schneiderkamplab/SDU-Daisy` (Hugging Face), the group's own Inspect task
   (`dfm_evals/tasks/daisy.py`) loads that repo's `train` split, that split has had 592 rows since its single upload
   on 10 Feb 2026, and the report says "on full datasets". 9.6% EM of 592 is 57 correct answers; our 5.6% is 33.
   The DAISY paper's own table (741 questions) reports only F1 and BLEU, never EM.
2. **Their scorer is byte-for-byte what we vendored, including the ASCII-only normaliser.** `normalize_text` keeps only
   `[a-z0-9]`, so æ, ø, å and every accented letter are deleted on both sides before EM, F1 and BLEU. The Inspect
   port has a unit test asserting `normalize_text("ÆØÅ 123") == "123"`. Their generation setting for Daisy is
   `max_tokens=100`, `temperature=0.0`, the Danish template as a single user message, no system prompt, no shots.
3. **The llama.cpp port we run Mimir on is causal-only; Mimir is a prefix-LM.** `config.json` has `"prefix_lm": true`;
   PR ggml-org/llama.cpp#27625 states "causal attention only - the upstream prefix-LM mode is not implemented" and
   reports 95.8% top-1 agreement with the reference at q8_0. The transformers implementation applies bidirectional
   attention over the prompt only when `token_type_ids == 1` is passed for the prompt tokens. This is the first
   mechanism to test for the 5.6 vs 9.6 gap (Section 3.2).
4. **Their harness is Inspect AI (AISI) via the `dfm-evals` package, greedy, seed 4242, 0-shot for all Danish tasks,
   `max_tokens=1` for multiple choice and 2048 for generation; the DAISY paper itself used an OpenAI-compatible
   endpoint with the same prompt and 100 tokens.** EuroEval is used separately (Dynaword, DaLA, Encoder vs Decoder,
   Munin releases) with few-shot prompting and bootstrap confidence intervals.
5. **The most valuable unrun apple is Multi Wiki QA (Danish), their reading-with-context task.** Mimir 66.8 EM,
   Gemma 3 1B 42.6, Qwen 3.5 0.8B 41.6, OLMo 2 1B 8.4 (Mimir Table 9), 0-shot, 32 tokens, "svar med maks. 3 ord",
   SQuAD-style EM. It is exactly our "reading fidelity" question measured their way, and it runs on the 1060.

---

## 1. Paper-by-paper cards

Cards are grouped by relevance to a QA-with-lookup study. Each card: venue, id, one-line contribution, benchmarks,
metrics with definitions, models, decoding, cost, tool or retrieval numbers, and the rows we could compare against.

### 1.1 The Danish model and benchmark line (the ones we build on)

#### DFM Mimir v1: An Open HRM Delivering Frontier Performance at 1B Parameters Using Only Permissible Post-Training Data
- Technical report, arXiv 2608.13517 (v1 13 Aug 2026, v2 20 Aug 2026 adds memorisation audits). Schneider-Kamp,
  J. Nielsen, Barmina, Enevoldsen (AU), Galke Poech. Model: `danish-foundation-models/DFM-Mimir` (Apache 2.0).
- Contribution: a 1B Hierarchical Reasoning Model trained from scratch on 161 permissible post-training datasets;
  claims state of the art for Danish at 1B and competitiveness with Qwen 3.5 4B and Gemma 4 E2B on 20 benchmarks.
- Architecture (Section 4, config.json): hidden 1536, 12 heads, head_dim 128, 16 layer slots, vocab 262,144
  (Gemma-4 tokenizer), H_cycles 2, L_cycles 3, truncated backprop 5 steps, `prefix_lm: true`, max positions 4096,
  1.3B non-embedding + 0.4B embedding parameters. Trained with a Gemma-4 style chat template from scratch.
- Training (Table 6): 70,479,308,606 tokens per epoch, 161 datasets, English 68.62%, Danish 24.74%, bilingual 6.54%;
  lr 3e-4 with 2,000-step warm-up then constant, AdamW (0.9, 0.95), wd 0.1, EMA 0.9999, global batch 262,144 tokens
  (4 contexts of 4,096 per accelerator, 2 accumulation steps, 8 accelerators), 1.65M steps (model card says
  1,750,000), 8x NVIDIA B200 180 GB, just under 3 weeks at ~1.1 s/step. No FLOPs figure.
- Agentic and tool-use training data (Section 3): "Agentic & tool use" category 6.66B tokens (9.46%, 8 datasets);
  tool-call formatted data 1.87B tokens (2.65%); nvidia/Nemotron-SFT-Agentic-v2 4.27B (6.06%);
  allenai/Dolci-Instruct-SFT-Tool-Use 1.61B (2.29%). The chat template (`chat_template.jinja`) has native tool
  definition and tool-call rendering (Gemma-4 syntax). No tool-use benchmark is reported.
- Evaluation setup (Section 5, quoted): "All benchmarks were evaluated at temperature 0 (greedy decoding) with
  shuffle seed 4242 on full datasets. All models used vLLM-served endpoints with FlashInfer, with the exception of
  Mimir, which requires FlashAttention to correctly capture the PrefixLM and Gemma 4 chat template. We ran both vLLM
  with FlashAttention4 and Hugging Face Transformers, obtaining comparable results up to numerical stability. For the
  ease of reproduction, we report the results from Hugging Face Transformers. Some English benchmarks use few-shot
  prompting ... All Danish tasks are 0-shot. MCQ tasks use max_tokens=1 ... All non-MCQ tasks (or whenever reasoning
  is enabled) use max_tokens=2048. All baseline evaluations were conducted via the Inspect AI Framework."
- Table 11 (benchmark, dataset, shots): BoolQ google/boolq 5; Winogrande allenai/winogrande 5; Hellaswag
  Rowan/hellaswag 10; MMLU cais/mmlu 5; ARC-C allenai/ai2_arc 25; DROP EleutherAI/drop 3; GovReport ccdv/govreport 0;
  GSM8K openai/gsm8k 0; MATH EleutherAI/hendrycks_math 0; HumanEval 164 problems 0; Angry Tweets DDSC/angry-tweets 0;
  DaLA giannor/dala 0; GEC-DaLA giannor/dala_gen_v3 0; PIQA-da local JSON 0; Daisy schneiderkamplab/SDU-Daisy 0;
  Multi Wiki QA oliverkinch/multi-wiki-qa 0; WMT24++ EN-DA synquid/wmt24pp 0; Nordj. News alexandrainst/nordj-news 0;
  IFEval-Da danish-foundation-models/ifeval-da 0; Hellaswag-da EuroEval 0.
- Table 9, Danish (metric per column: Angry Tweets acc, DaLA F1, GEC EM, PIQA acc, Daisy EM, WikiQA EM, WMT chrF,
  N.News chrF, IFEval-da acc, Hellaswag-da acc, Avg):

  | Model | AngryTw | DaLA | GEC | PIQA | Daisy | WikiQA | WMT | N.News | IFEval | HSwag-da | Avg |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | Mimir 1B | 67.4 | 96.1 | 85.6 | 53.7 | 9.6 | 66.8 | 53.9 | 35.87 | 63.9 | 35.3 | 56.8 |
  | HRM-Text 1B | 42.4 | 26.7 | 0.5 | 13.0 | 0.0 | 34.9 | 25.4 | 26.76 | 18.5 | 28.8 | 21.7 |
  | Qwen 3.5 0.8B | 53.8 | 51.0 | 0.7 | 56.5 | 0.7 | 41.6 | 37.8 | 35.30 | 39.6 | 25.0 | 34.2 |
  | Gemma 3 1B | 54.4 | 41.0 | 3.3 | 72.2 | 1.4 | 42.6 | 45.1 | 35.56 | 47.2 | 24.8 | 36.8 |
  | OLMo 2 1B | 33.6 | 48.7 | 0.2 | 75.0 | 0.0 | 8.4 | 30.0 | 33.77 | 32.5 | 26.7 | 28.9 |
  | Qwen 3.5 2B | 61.6 | 36.4 | 8.0 | 25.0 | 2.5 | 49.4 | 45.6 | 34.85 | 56.1 | 24.7 | 34.4 |
  | SmolLM3 3B | 63.2 | 33.5 | 3.3 | 51.9 | 2.2 | 0.3 | 37.3 | 35.98 | 49.8 | 40.1 | 31.7 |
  | Qwen 3.5 4B | 69.1 | 50.1 | 42.6 | 70.4 | 4.7 | 57.1 | 52.1 | 37.03 | 73.7 | 34.7 | 49.2 |
  | Gemma 4 E2B | 64.6 | 56.7 | 36.9 | 46.3 | 5.6 | 44.1 | 55.2 | 35.67 | 75.5 | 25.6 | 44.6 |
  | Gemma 4 E2B (think) | 67.7 | 66.8 | 23.4 | 63.9 | 5.1 | 59.3 | 56.0 | 36.30 | 81.2 | 39.0 | 49.9 |
  | Munin-Apertus 8B | 60.6 | 46.1 | 42.1 | 81.5 | 12.5 | 49.9 | 55.8 | 30.30 | 53.0 | 24.5 | 45.6 |
  | Munin-Mistral 8B | 61.3 | 48.8 | 26.4 | 76.9 | 8.4 | 48.4 | 51.8 | 32.92 | 67.8 | 33.6 | 45.6 |
  | Munin-Qwen 9B | 69.1 | 60.6 | 11.4 | 38.9 | 5.4 | 55.7 | 56.1 | 35.89 | 71.8 | 34.3 | 43.9 |

  The paper's only sentence on these: "On the Danish benchmarks, Mimir outperforms all competitors on grammatical
  tasks (DaLA, GEC), question-answering tasks (WikiQA), and is close to the best on Nordjylland News." No discussion
  of why Daisy is low for every model. The model card ships `plots/subject_avg_scores.png`, so they do look at Daisy
  per Subject.
- Table 7, English (Mimir row): BoolQ 87.8, Winogrande 73.5, Hellaswag 67.3, MMLU 57.5, ARC-C 81.6, DROP 83.1 (F1),
  GovReport 32.0 (R1), avg 69.0. Table 8, Math and code: GSM8K 89.9, MATH 45.8, HumanEval 56.7. Gemma 4 E2B thinking
  needs ~500 to 650 tokens; its thinking is stripped with vLLM `--reasoning-parser gemma4` before scoring.
- Memorisation audits (Appendix C, Tables 12 and 13): 500 prefix-attack prompts per source category with 50-token
  prefixes; verbatim 50+ token spans in 0.00022% to 0.015% of checked documents per category; second audit
  136,612,444 model-input evaluations, 5,562 exact 64+64 matches (0.0041%), 61 coherent prose, 1 expressive prose,
  "no high-priority copyright findings".
- Stated future work (Section 7): scaling behaviour of HRMs; "the capabilities as an assistant are still limited
  compared to the state of the art. This calls for future work in this capacity, including reinforcement learning,
  which is yet unexplored for this architecture." No retrieval, RAG, calibration, abstention or uncertainty content.
- Not in the paper: an inference-cost comparison against a standard 1B transformer (the HRM unrolls 2x(3+1)=8 passes
  over 2 stacks; our measured 4.2 tok/s decode on the 1060 vs 86 tok/s for Llama 3.2 1B is the only number we have).

#### SDUs DAISY: A Benchmark for Danish Culture
- arXiv 2601.19930 (11 Jan 2026), J. Nielsen, Beltoft, Schneider-Kamp, Galke Poech. Code
  github.com/schneiderkamplab/SDU-Daisy (README says 746 pairs; paper says 741; HF release has 592 with gold).
- Contribution: closed-ended Danish QA over the 108 works of the Danish Culture Canon 2006 (8 domains, 12 works each,
  6 pages omitted for missing or incomplete Wikipedia pages); questions generated by Gemma 3 27B in 4-bit ("generate
  5 random questions" per work, "stikprøvekontrol" sampling of central and peripheral facts), then human-approved or
  corrected; answers "korte og præcise, helst et enkelt ord eller en kort sætning".
- Metrics (Section 3.2): word-level precision, recall and F1 after "case normalization, remove punctuation, articles
  and extra white space"; BLEU via NLTK `sentence_bleu` with `SmoothingFunction().method4`. EM is not named in the
  paper, but `evaluation/eval.py` computes it and the Mimir report reports it. Note that the actual normaliser is
  `re.sub(r"[^a-z0-9]+", " ", s.lower())`, which removes Danish letters and does not remove articles despite the
  docstring.
- Protocol: zero-shot, the Danish "Prompt Template Version 1" (Appendix B, identical to `PROMPT_TEMPLATE` in eval.py)
  as one user message via an OpenAI-compatible chat endpoint, `max_tokens=100`, `temperature=0.0` (from eval.py; the
  paper itself gives no decoding numbers and notes gpt-oss-20b sometimes needs a >2000-token reasoning trace).
- Table 2 (741 questions, BLEU / F1): gpt-oss-20b 0.062 / 0.112; gpt-oss-120b 0.126 / 0.211; gemma-3-27b-it
  0.123 / 0.193; Llama-3.3-70B-Instruct 0.166 / 0.268; Mistral-Small-3.1-24B-Instruct-2503 0.124 / 0.202. Our
  rescoring of their released prediction files on the 592 public golds: Llama-3.3-70B EM 0.225 / F1 0.277 / BLEU
  0.172; gpt-oss-120b 0.171 / 0.218 / 0.131; Mistral-Small 0.169 / 0.217 / 0.134; gemma-3-27b 0.171 / 0.203 / 0.132;
  gpt-oss-20b 0.074 / 0.110 / 0.064 (results/RESULTS.md).
- Failure discussion (Section 5): scores are low because of "limited representation of Danish-language and
  Denmark-specific content within the overall training data distribution, where such nationally bounded knowledge
  constitutes a relatively weak signal", and "preference alignment and safety tuning may further bias models toward
  cautious, generalized responses". Tables 1 and 3 give anecdotes only; no error counts, no per-domain counts.
- Limitations (Section 7): scope bounded by the Canon; "we are dependent on a prompt ... This prompt is not
  necessarily optimal for all model ... We plan to iterate". No retrieval, open-book, RAG or tool baseline anywhere.
- Hidden-apple status: their five rows are on 741, ours on 592; EM for their five models exists only in our rescoring.

#### Training Language Models to Use Prolog as a Tool
- ACL 2026 Findings, arXiv 2512.07407 (v1 8 Dec 2025, v3 25 Jun 2026). Mellgren, Schneider-Kamp, Galke Poech.
  Code github.com/aisilab/Prolog-as-a-Tool; data `niklasm222/gsm8k-prolog-prover` (7,473 rows: instruction, input,
  output; 15 corrected errors, 14 in openai/gsm8k). Checkpoints on HF under `niklasm222/` include
  `Qwen2.5-3B-Instruct-GRPO-2K-gsm8k-prolog`, a sweep `qwen2.5-3b-grpo-1.7k-gsm8k-prolog-v1 ... v14-rwd4`,
  `qwen2.5-3b-1.75k-prolog-sp-struct-rwd1`, `gemma-2-2b-it-gsm8k-prolog-sft-lora-v1`, and
  `llama-3.2-1b-it-GRPO-gsm8k-prolog` (a 1B GRPO tool user, undocumented).
- Contribution: GRPO fine-tuning of Qwen2.5-3B-Instruct to emit Prolog that an external SWI-Prolog executes; varies
  prompt structure (SP-Base, SP-Struct, SP-Declare, SP-Reflect), reward suite (Rwd1 to Rwd3) and inference protocol
  (single-try, multiple-try N=20, agentic-internal, agentic-independent); identifies an accuracy vs auditability
  trade-off framed as reward hacking.
- GRPO recipe (Section 4, Appendix B): 4-bit quantised Qwen2.5-3B-Instruct + LoRA (unsloth + TRL per the HF tags),
  one 40 GB GPU, 1 epoch over 1,750 training problems (375 val, 375 test from a 2,500 subset), AdamW, batch 8,
  lr 5e-6 cosine, wd 0.1, grad clip 0.1, fixed seeds. Rewards: correctness (exact match 2.0, numeric-but-wrong 1.0,
  executable 0.5), Prolog syntax up to 1.0, format soft 0.5 and strict 0.5, XML tags 0.125 each; Rwd2 adds
  Sentence-BERT (all-MiniLM-L6-v2) similarity plus predicate overlap; Rwd3 adds curriculum weighting (sigmoid k=12,
  tau=0.5), structure reward, 0.2x hard-coding penalty. Tool interface (Appendix C):
  `{"name": "run_prolog", "arguments": [{"code": "string"}]}` declared in the system prompt.
- Inference: temperature 0.2 throughout; agentic modes up to 20 turns, "temperature shake" 1.15x capped at 0.3 on
  repeated or empty generations, context compression at 95% of a 2048-token budget; per-turn token accounting in
  the logs ("used=622 (32.9%) | rem=1268 | budget=1890").
- Metrics (Section 4): accuracy = output parses as int or float and equals ground truth; structural validity = at
  least one user-defined predicate other than solve/1 and at least one arithmetic constraint; semantic similarity =
  cosine over SBERT plus predicate-name overlap, 0 to 100%.
- Numbers: Table 2 (val, 375): best 89.87% (SP-Struct + Rwd1 + multiple-try). Table 4: best GRPO 90% vs best SFT 79%
  on val, "56% higher accuracy scores than SFT baseline on average across inference methods". Table 5 (official
  GSM8K test, 1,320): 80.21% (full-data model, multiple-try), 78.24% (subset model); DeepSeekMath-7B-RL 86.7%.
  Table 6 (zero-shot, 375 samples each): MMLU-STEM single 50.93, multiple 53.60, agentic-internal 56.80,
  agentic-independent 58.13; MMLU-Pro 21.33 / 26.67 / 30.67 / 29.33; 7B few-shot baselines DeepSeekMath 56.50
  (STEM), Mistral 51.10 (STEM), Gemma 33.70 (MMLU-Pro). Trade-off (Figure 2): SP-Struct-Rwd1 89.87% accuracy with
  1.60% structural validity; SP-Declare-Rwd3 62.40% with 90.40%.
- Cost: no GPU hours; the 40 GB card and the 2048 budget are the only resource numbers.
- Relevance: this is the ad's "agentic behaviour and tool use" topic in their hands; their notion of "agentic" is a
  bounded generate-execute-reflect loop with a hard turn budget and reset, evaluated at temperature 0.2, not greedy.

#### DaLA: Danish Linguistic Acceptability Evaluation Guided by Real World Errors
- LREC 2026, arXiv 2512.04799. Barmina, Norman, Schneider-Kamp, Galke Poech. Data `giannor/dala`, `dala_medium`,
  `dala_large`, `dala_gen_v3` (GEC variant used by dfm-evals) and EuroEval/dala.
- 14 corruption types derived from real Danish learner errors applied to UD Danish sentences (Algorithm 1, one error
  per sentence, corruption precision 0.957, Table 1). Sizes (Section 3.5): DaLA 512/128/1024 pairs (1024/256/2048
  sentences); medium 4592/386/2678 pairs; large 6124/384/1148 pairs.
- Protocol (Section 5.1): EuroEval, encoders fine-tuned, generative models few-shot (12 examples), evaluation runs
  raised from 10 to 50; metrics MCC (primary) and unweighted macro-F1 with CIs.
- Table 2 (ScaLA MCC / F1, DaLA MCC / F1): electra-small-da 70.37 / 84.82, 65.36 / 81.97; roberta-large-1160k
  75.04 / 87.19, 71.50 / 85.13; dfm-sentence-encoder-large 70.29 / 84.60, 74.19 / 86.18; gemma-3-27b-it
  60.10 / 79.67, 56.77 / 78.14; gemma-3-12b-it 56.74 / 77.59, 50.66 / 75.02; gemma-3-27b-pt 62.46 / 80.97,
  59.78 / 79.56; gemma-3-12b-pt 57.32 / 77.28, 53.93 / 75.80; qwen3-32b 60.07 / 79.10, 45.22 / 72.43; qwen3-14b
  54.50 / 74.71, 40.71 / 69.26. No 1B to 4B generative rows. No cost numbers.
- dfm-evals 0-shot version (`dala.py`): prompt "Sætning: {text}\n\nBestem om sætningen er grammatisk korrekt eller
  ej. Svar kun med ja eller nej, og intet andet.", 8 tokens, temperature 0, macro-F1 and MCC. Mimir 96.1 F1 in Table 9
  is this 0-shot setting, not the paper's few-shot EuroEval setting.

#### Dynaword: From One-shot to Continuously Developed Datasets
- LREC 2026, arXiv 2508.02271. Enevoldsen et al. with Barmina, J. Nielsen, Galke, Schneider-Kamp (17 authors).
  Data `danish-foundation-models/danish-dynaword` (v1.2.7, 4.8B Llama-3 tokens, 40+ sources, openly licensed).
- Experiments (Section 4.1, Table 2): Gemma-3-1B continually pre-trained or trained from scratch on Gigaword vs
  Dynaword-matched vs Dynaword-full; perplexity on six Danish sets (DDT, JVJ, Synnejysk, Nordjylland, Wiki-dan, DR)
  improves 1.2% to 13% (CPT) and 12% to 42% (scratch); downstream via EuroEval (sentiment, NER, RC, knowledge; MCC,
  micro-F1, BERTScore, ROUGE-L, accuracy). Training: sequence length 6144, effective batch 32, cosine; no GPU hours.
  The six checkpoints are public (`gemma-3-1b-cpt-dynaword-full-v1` etc.).

#### Encoder vs Decoder: Comparative Analysis of Encoder and Decoder Language Models on Multilingual NLU Tasks
- NoDaLiDa 2025, arXiv 2406.13469 (v2 Jan 2025). D. Saattrup Nielsen, Enevoldsen, Schneider-Kamp.
- ScandEval (now EuroEval) across 8 Germanic languages; few-shot decoders: 8 shots NER, 12 sentiment and LA, 4 QA;
  10 bootstrap iterations with resampled shots; structured generation via `outlines`; QA prompt ends with "Answer in
  max 3 words"; Mean Rank Score aggregation (Appendix B). Danish QA = ScandiQA-da (1,024 / 256 / 2,048).
  Danish leaderboard excerpt (Table 4): GPT-4-0613 1.24, GPT-4-1106 1.25, DanskGPT-Chat-Llama3-70B 1.29,
  RoBERTa-large-1160k 1.39. Encoders win NLU at a fraction of the parameters. No cost numbers.

#### SommBench: Assessing Sommelier Expertise of Language Models
- LREC 2026, arXiv 2603.12117. Brach et al. with J. Nielsen, Barmina, Schneider-Kamp, Galke Poech (13 authors).
- 3,024 examples, 8 languages incl. Danish: WTQA (1,024 MCQ, 128 per language, single letter, exact match), WFC
  (1,000 wines, JSON field completion, exact match on categorical fields, MAPE <= 55% on numeric), FWP (1,000
  English pairings, yes/no, MCC with TPR/TNR). Zero-shot, temperature 0, reasoning off for Qwen.
- Table 1 (WTQA / WFC / FWP / score): gemini-2.5-flash 0.90 / 0.63 / 0.39 / 0.65; gpt-4.1 0.90 / 0.62 / 0.25 / 0.59;
  gpt-5 0.97 / 0.57 / 0.17 / 0.57; qwen3:30b 0.84 / 0.48 / 0.20 / 0.51; qwen3:8b 0.64 / 0.43 / -0.08 / 0.33;
  **qwen2.5:3b 0.48 / 0.24 / 0.10 / 0.27**. Table 2 Danish WTQA: gpt-5 0.98, llama3.1:8b 0.61. Finding: a strong
  positivity bias in pairing judgements (gpt-4o-mini approved 86% of a 50/50 set). No RAG, calibration or abstention.

### 1.2 Evaluation, safety and calibration line (methods we can borrow)

#### LLMs Can Leak Training Data But Do They Want To? A Propensity-Aware Evaluation of Memorization in LLMs
- arXiv 2606.06286 (4 Jun 2026). Barmina, Schneider-Kamp, Galke Poech.
- Separates capability (prefix attack: condition on the first 50 tokens of a real training example) from propensity
  (100 generic and 100 specific "plausible real-world prompts" generated by GPT-5.5 with low lexical overlap).
  Propensity metric (Eq. 1): PM = 1/2 (1 + (f_p - f_c) / (f_p + f_c)), 0 = high capability but no propensity,
  0.5 = same behaviour in both settings. Metrics NVR, FMR, ALS (verbatim rate, first-match rate, average longest
  span). Greedy decoding. Models: Comma 7B (Common Pile, 463.6B tokens) and DFM Decoder 7B (continual pre-training of
  Comma over 30B tokens, two-thirds Dynaword). Table 4: DFM on Dynaword generic PM_NVR 0.0263, on Common Pile 0.0134.
  Tracing cost: ~1 min per 100 queries on 4 CPU cores over 460B tokens. The capability vs propensity framing maps
  directly onto our agentic (free-form) vs scaffold (forced decision) conditions.

#### Confidence and Calibration of Activation Oracles for Reliable Interpretation of Language Model Internals
- arXiv 2605.26045 (May 2026, v2 3 Aug 2026). Torrielli, Schneider-Kamp, Galke Poech.
- Five confidence estimators for LoRA "activation oracles" on Qwen3-8B, Qwen3.6-27B, Gemma-2-9B, Gemma-3-27B:
  (M1) log-probability of the answer tokens, (M2) bootstrap k=20 samples at temperature T with confidence = frequency
  of the mode, (M3) direct numeric "On a scale of 0-100, how confident are you?", (M4) constrained five-label
  decoding scored by logits, (M5) forced choice over all candidates. Metrics: ECE with 10 equal-width bins, Brier,
  NLL, AUROC, selective prediction; post-hoc temperature, Platt, isotonic and beta calibration (Tables 6 to 9);
  bootstrap reaches 70% of its value at k=10 (Table 10). Table 1: forced-choice AUROC 0.940 to 0.959; bootstrap ECE
  0.040 to 0.147. This is the group's calibration vocabulary; we have measured none of it yet.

#### PsychoSafe: Eliciting Psychologically-Informed Refusals in Large Language Models
- arXiv 2606.09697 (Jun 2026). Barmina, Torrielli, Harms, J. Nielsen, Mächtle, Beltoft, Schneider-Kamp, Eisenbarth,
  Galke Poech, Lauscher. Qwen3.5-27B, LoRA SFT (r=1, alpha 32, lr 1e-4 cosine, batch 4, 5 epochs, 4,096 tokens, one
  H100) on 8,019 pairs; LLM judge (Qwen3.5-397B-A17B) chosen by agreement with one human expert on 50 items
  (kappa 0.61 vs 0.58 and 0.56). Table 1: v0 base overall 71.9 vs v1 prompt 92.0 (+28.1 points). SORRY-Bench
  compliance 17.1% to 0.0%; XSTest over-refusal 13.2% (default) vs 24.0% (v1) on the base model. Capability retention
  MMLU 0.8443 to 0.8020. Relevant for its judge-selection recipe (agreement with humans before trusting a judge).

#### The Arbiter Agent: Continually Monitoring Multi-Agent Conversations to Detect Emergent Misalignment
- AITC 2026, arXiv 2606.10747. Tonini, Torrielli, Lautrup, Schneider-Kamp, Çelikok, Galke Poech.
- A budget-constrained auditor agent chooses among cost-priced actions (observe, ask, inspect system prompt or CoT
  at fixed cost 5, log incident; lambda 0.005 per word), 3 agents x 30 turns, n=20 replications, micro-F1 over
  agents, detection turn t*, budget used. Table 2: pure observation F1 0.12 vs interrogation + log 0.51 on
  weight-induced misalignment; Table 3: 0.97 F1 with the full action set on instruction-induced cases; Table 7:
  backbone DeepSeek-v3.2 vs Qwen3.6-plus. Useful as a template for pricing tool calls and reporting mean +- SEM.

#### Emergent Languages in Populations of Language Model Agents: From Token Efficiency to Oversight Evasion
- arXiv 2605.31170 (May 2026). Beltoft, Brach, Torrielli, J. Nielsen, Pirchert, Tonini, Schneider-Kamp, Galke Poech.
  518 constructed-language proposals from Moltbook; alignment and coherence 0 to 100 judged by DeepSeek-V3.2 at
  temperature 0 (Table 2: oversight-evasion 61.92 vs token-efficiency 77.35 alignment); in-context learnability 1 to 5
  by two generator and two judge models (2,072 judgements, Spearman 0.29 to 0.30 between judges, self-preference
  bias of 0.72 points). Honest about judge calibration limits (Section 6.1).

#### The Moltbook Files: A Harmless Slopocalypse or Humanity's Last Experiment
- arXiv 2605.07462 (May 2026). Brach, Torrielli, Beltoft, Pirchert, Schneider-Kamp, Galke Poech. 232,497 posts and
  2,202,950 comments from an agent-populated platform, PII-scrubbed with Presidio; fine-tuning Qwen2.5-14B-Instruct on
  it drops TruthfulQA MC1 36.60 to 18.73 (Reddit control 21.42), alignment 93.12 to 92.50 (Reddit 86.88), coherence
  99.38 to 94.38 (Section 5.2, CIs as 1.96 SE).

#### The Energy Society: A Simulation Environment for Studying Agent Cooperation under Survival Pressure
- AITC 2026, arXiv 2607.14865. Hansen, Torrielli, Tonini, Galke Poech. Five agents (Gemma4-E4B, Nemotron-3-Nano-4B,
  Qwen3.5-4B, Qwen3-8B, Qwen3.5-9B) pay energy per generated token, C = k T S^alpha with k 0.015, alpha 0.5, earn it by
  solving MMLU-Pro jobs; LangChain tool calls, LangGraph loop; metrics survival rounds, efficiency ratio, collisions,
  donations; 5 seeds. Section 6.1: large models spend 329.9 to 451.1 energy per round vs 104.1 to 140.2 for 4B
  models. A ready-made way to price "tokens times sqrt(parameters)" for our cost table.

#### Super-additive Cooperation in Language Model Agents
- FAIEMA 2025, arXiv 2508.15510. Tonini, Galke. Iterated prisoner's dilemma tournaments with Qwen3 14B, Phi-4
  reasoning, Cogito 14B; cooperation rate and one-shot cooperation with 95% CIs (Table 3: Qwen3 RI 0.22, GC 0.23,
  SA 0.32); neutral action names to avoid training bias.

#### Guarded Query Routing for Large Language Models (ECAI 2025, arXiv 2505.14524) and Influence of Prompt Engineering on Small Language Models for Guarded Query Routing (arXiv 2607.24801)
- Šléher, Brach, Sloboda, Košťál, Galke; second paper Šléher, Brach, Košťál, Galke Poech (Jul 2026).
- GQR-Bench: 3 in-domain sets (law, finance, health) plus 7 OOD sets; GQR-Score = harmonic mean of ID and OOD
  accuracy. Table 2 (2025): Llama3.1:8B 91.67, GPT-4o-mini 91.61, WideMLP 87.74, fastText 80.12, BGE + SVM 82.94;
  Table 4 latency per query: fastText 0.00009 s, WideMLP 0.00359 s, Llama3.1:8B 0.06275 s, GPT-4o-mini 0.6668 s.
  2026 paper: 22 models 270M to 70B with greedy vLLM on two RTX 4090; best unoptimised Gemma 3 27B 96.01; best
  optimised Qwen3.5 9B 95.74 (DSPy BootstrapFewShot); GEPA with a gpt-5.4 teacher; latency 0.02 to 0.05 s standard,
  0.05 to 0.28 s with optimised prompts; "mean single-request inference time over the full test split, warm-start,
  one request in flight" (Section 3.2). That latency definition is the one to copy.

#### Chain of Summaries: Summarization Through Iterative Questioning
- arXiv 2511.15719 (Nov 2025). Brach, Košťál, Galke Poech. Iteratively refine a summary by generating questions and
  fixing gaps; evaluate by QA over the summary (Correct-F1 from TriviaQA). Table 1: GPT-4o-mini CoS 0.80 vs original
  content 0.76 vs zero-shot 0.73; **Llama3.2:3B CoS 0.62 vs original content 0.51**; Qwen2.5:7B 0.60 vs 0.41.
  Table 7 cost: indexing ~133k tokens ($0.022), 9,830 tokens saved per query (98.3%), break-even 13 to 15 queries.
  A published Llama 3.2 3B QA-over-context F1 exists here, but on an English TriviaQA subset with unspecified splits.

#### Isolating Culture Neurons in Multilingual Large Language Models
- IJCNLP-AACL 2025 Findings, arXiv 2508.02241. Namazifard, Galke Poech. MUREL corpus, 85.2M tokens, six cultures
  incl. Danish (11,383k tokens); LAPE over 100M Wikipedia tokens per language and CAPE over 10M MUREL tokens per
  culture; 56.7% of culture neurons are language-independent; ablating them accounts for 76.3% of the effect; 280 GPU
  hours. Models Llama-2-7b, Llama-3.1-8b, Qwen2.5-7b, Gemma-3-12b. No QA benchmark.

#### ChronoMedKG (arXiv 2605.22734) and The Provenance Gap in Clinical AI (arXiv 2604.17114)
- Ahmed, ..., Galke Poech, Röttger (Baumbach on the first). Evidence-traceable temporal knowledge graphs for clinical
  reasoning; ChronoTQA 3,341 questions in 8 task types; frontier LLMs drop ~30 points from static to temporal
  questions; graph retrieval "rescues 47 to 65% of their long-tail failures"; best model cites 15.3% relevant PMIDs
  unaided vs 100% evidence verifiability with the graph. This is the group's one retrieval-with-provenance line.

#### Interview Bot: Can Agentic LLM's Perform Ethnographic Interviews?
- ICAART 2025 (SciTePress, pp. 702 to 709). Beltoft, Schneider-Kamp, Askegaard. Qualitative; no metrics.
  Repo schneiderkamplab/interviewbot (Gradio UI over local model formats).

#### Not Everything That Counts Can Be Counted: A Case for Safe Qualitative AI
- FAIEMA 2025, arXiv 2511.09325. Beltoft, Galke. Position paper; no experiments.

### 1.3 Systems and architecture line (their compute and cost vocabulary)

#### DeToNATION: Decoupled Torch Network-Aware Training on Interlinked Online Nodes
- AAAI 2026 main track, arXiv 2502.06728 (v1 as FlexDeMo, Feb 2025). From, J. Nielsen, Galke Poech, Schneider-Kamp.
  Hybrid-sharded training that syncs only fast momentum components across nodes; T5-base on Opus Books, ViT-B on
  CIFAR-100, OLMo2-1B on Dolma v1.6; results as loss curves, not tables; OLMo2 on 22 nodes x 4 A100 64 GB, 10K steps;
  bandwidth 1070 Mbps full replication vs 291 (DeMo) vs 152 (random); "2.6 times faster than Hybrid-FSDP with AdamW".
  No Danish evaluation.

#### FlexMoRE: A Flexible Mixture of Rank-heterogeneous Experts for Efficient Federatedly-trained Large Language Models
- arXiv 2602.08818 (Feb 2026). Pirchert, J. Nielsen, From, Galke Poech, Schneider-Kamp. Post-hoc LoRA (SVD) extraction
  of FlexOlmo experts with per-expert rank; 120 tasks in 6 groups (MC9, GEN5, AGIEval, BBH, MMLU, MMLU-Pro), unweighted
  mean of group means. Table 2: FlexMoRE-a2 heterogeneous 10.75B params avg 0.4710 vs FlexOlmo-a2 33.27B 0.4465
  (+5.49%); a7 variant +14.08%. No shots, prompts, cost or Danish. Code schneiderkamplab/FlexMoRE.

#### Write Once, Run Everywhere: The Axon DSL for Shape-Safe and Framework-Agnostic LLM Architectures
- arXiv 2608.19889 (20 Aug 2026). J. Nielsen, Namazifard, Galke Poech, Schneider-Kamp. A typed DSL compiling one
  architecture spec to PyTorch, JAX, MLX, vLLM; 204+ checkpoints, 60 families, 135M to 32B; median runtime ratios
  0.804x (<=4B decoders), 0.631x on vLLM, 0.483x on MLX; 9.6% faster training steps on Gemma-3 270M. No accuracy
  benchmarks, no Mimir mention.

#### BrainSurgery: Reproducible and Reliable Declarative Weight Manipulations for Model Editing and Upcycling
- arXiv 2606.09707 (Jun 2026). Barmina, Pirchert, Blasi Núñez, Galke Poech, Schneider-Kamp. YAML plans for tensor
  edits with assertions; 50-prompt inference-preservation check (cosine 1.0, perplexity ratio 1.01, top-1 100%).
  No benchmarks.

#### BitNet trio: BitNet b1.58 Reloaded (DeLTA 2024, arXiv 2407.09527), When are 1.58 bits enough? (ICAART 2025, arXiv 2411.05882), Continual Quantization-Aware Pre-Training (ACL 2025 Findings, arXiv 2502.11895)
- J. Nielsen, Galke, Schneider-Kamp. Ternary-weight QAT for 100K to 48M models (perplexity, MNIST, CIFAR), for
  WideMLP, GCN, BERT, T5 and OLMo 1B (Table 1 of 2411.05882: WideMLP-b1.58 82.24% vs 83.03%), and for when to switch
  16-bit to 1.58-bit during OLMo-1B pre-training on Dolma (10K steps of 4M tokens; Table 1 of 2502.11895 gives
  11 zero-shot tasks, e.g. HellaSwag 0.3212 full 1.58-bit vs 0.3607 full 16-bit vs 0.3375 hybrid). Validation loss on
  an internal 6.2M-document corpus, 80% Danish. No GPU hours. Code schneiderkamplab/bitlinear.

### 1.4 Peripheral 2023 to 2026 items (one line each, from dblp and arXiv; not read in full)

| Item | Venue | Note |
|---|---|---|
| Disjoint Generation of Synthetic Data (Lautrup, Rajabinasab, Hyrup, Zimek, Schneider-Kamp) | TMLR June 2026, arXiv 2507.19700 | Tabular synthetic data only (CTGAN, TabDiff, synthpop); no language models. This is the "synthetic data TMLR 2026" item. |
| SynthEval (Lautrup, Hyrup, Zimek, Schneider-Kamp) | Data Min. Knowl. Discov. 2025, arXiv 2404.15821 | Tabular utility and privacy evaluation framework; repo schneiderkamplab/syntheval. |
| Sharing is CAIRing (Hyrup, Lautrup, Zimek, Schneider-Kamp) | Mach. Learn. Appl. 2024, arXiv 2312.12216 | Privacy metric principles for tabular synthetic data. |
| Systematic Review of Generative Modelling Tools and Utility Metrics for Fully Synthetic Tabular Data | ACM Comput. Surv. 2025 | Survey. |
| Synthesizers: A Meta-Framework for Tabular Synthetic Data | ICSOFT 2024 | Repo schneiderkamplab/synthesizers. |
| Hilbert-Schmidt Independence under Rényi DP (Hyrup et al.) | arXiv 2508.21815 | Fair and private tabular generation. |
| Randomized PCA Forest for Outlier Detection; Similarity Based on Resample Exposure; Semi-supervised Subspace Learning | arXiv 2508.12776; SISAP 2025 x2 | Zimek group outlier detection. |
| MLDataForge (Schneider-Kamp et al.) | RANLP 2025 | Dataset preprocessing for multimodal foundation-model training; repo schneiderkamplab/mldataforge. |
| Minimizing Sorting Networks at the Sub-Comparator Level | LPAR 2024 | Logic and verification line. |
| Four Shades of Life Sciences (Seidlmayer, Galke, Förstner) | arXiv 2507.03488 | 2,603-text disinformation dataset; BioBERT F1 0.9836; Mistral 7B zero-shot F1 0.038. |
| Efficient Continual Learning for Small LMs with a Discrete Key-Value Bottleneck (Diera, Galke, Karl, Scherp) | ICNLSP 2025, arXiv 2412.08528 | Encoder continual learning; runtime tables. |
| Tokenization and Morphology in Multilingual LMs: mT5 vs ByT5 (Dang, Raviv, Galke) | ICNLSP 2025, arXiv 2410.11627 | 17 languages, Danish not included. |
| Isotropy Matters (ESANN 2025); RADAr HTC decoder (ECAI 2024); XML is secretly HTC (arXiv 2411.13687); POWN (CoLLAs 2024); Gumbel-MPNN (ECAI 2025); GenCodeSearchNet (GenBench 2023); Open-World Lifelong Graph Learning (IJCNN 2023) | various | Galke's Kiel/Ulm-era text and graph work. |
| What makes a language easy to deep-learn? (Galke, Ram, Raviv) | Nature Communications 2023 | Compositional structure helps networks and humans alike. |
| Learning and communication pressures in neural networks (Galke, Raviv) | Language Development Research 2024 | Perspective. |
| ICNLSP 2025 proceedings | Odense, 25 to 27 Aug 2025 | Galke was proceedings editor; the group hosted the conference. |

### 1.5 Items in the brief that are not the group's, or could not be found

- **PrologMCP (arXiv 2606.14935)** is by Mensfelt, Prabhakaran, Haret, Trencsenyi and Stathis (Royal Holloway), a
  SKILLL workshop paper (Lisbon, 18 Jul 2026). It cites the Prolog-as-a-tool line but no Odense author is on it.
  Do not attribute it to the group.
- **"LM memorization/safety preprints"** resolve to 2606.06286 (memorisation), 2606.09697 (PsychoSafe), 2606.10747
  (Arbiter), 2605.31170 and 2605.07462 (emergent languages, Moltbook), 2605.26045 (calibration of oracles).
- **No paper by the group on retrieval-augmented generation for Danish, on abstention, or on tool-use evaluation
  in Danish exists** as of 4 Sep 2026. The nearest are the clinical knowledge-graph preprints (Galke as coauthor) and
  the dfm-evals `bfcl-v1-da` task (Danish translations of BFCL exec_simple prompts, unpublished numbers for small
  models; Munin 1.0 8B models report Tool Calling accuracy 52.40 / 43.10 Apertus, 75.00 / 49.20 Ministral,
  79.40 / 75.80 Qwen, original vs Munin, on foundationmodels.dk).
- **A Mimir number on EuroEval** does not exist: `danish-foundation-models/DFM-Mimir` is not on the EuroEval Danish
  leaderboard (checked leaderboards/danish_all.csv, 553 rows).
- **DFM datasets with no paper yet** that are hidden apples in waiting: `kaenguruen` (Danish MCQ maths),
  `global-piqa-da`, `laerebogen`, `ifeval-da`, `multi-ifeval`, `ai-arenaen` (a Danish chatbot arena with votes),
  `linguistic-quality`, `danish-wildchat4.8M`, `multilingual-gsm-symbolic` (16 languages incl. Danish; GPT-4 low
  effort 83.2% original vs 70.2% synthetic Danish accuracy on the card).

---

## 2. HIDDEN APPLES: published numbers we can match on identical terms

"Setting" is the exact published protocol. "1060" is feasibility on the GTX 1060 6 GB with llama.cpp or transformers.
Times assume the measured box speeds (Mimir 4.2 tok/s decode, 143 tok/s prompt; Llama 1B 86 tok/s; Llama 3B 35 tok/s).

| # | Benchmark and split | Their number(s) | Exact setting | 1060 | What we would run |
|---|---|---|---|---|---|
| A1 | Daisy EM, HF `schneiderkamplab/SDU-Daisy` train (592) | Mimir 9.6; Gemma 4 E2B 5.6 (5.1 think); Qwen 3.5 4B 4.7; Qwen 3.5 2B 2.5; SmolLM3 3B 2.2; Gemma 3 1B 1.4; Qwen 3.5 0.8B 0.7; OLMo 2 1B 0.0; HRM-Text 0.0; Munin-Apertus 8B 12.5; Munin-Mistral 8B 8.4; Munin-Qwen 9B 5.4 (Mimir Table 9) | Inspect `daisy` task: template as one user message, chat template applied, greedy, max_tokens 100, ASCII normaliser, EM = mean of per-row max over references | Done for 5 models (llama.cpp); Mimir via transformers sdpa fp16 fits (3.4 GB weights) but Pascal fp16 is slow: 592 x ~60 tokens is a few hours, or the Colab T4 path | Rerun Mimir closed-book in transformers with and without `token_type_ids=1` on the prompt; report both next to 9.6 with the 1.2-point SE |
| A2 | Daisy F1 / BLEU on 741 (DAISY Table 2) | Llama-3.3-70B 0.268 / 0.166; gpt-oss-120b 0.211 / 0.126; Mistral-Small-24B 0.202 / 0.124; gemma-3-27b 0.193 / 0.123; gpt-oss-20b 0.112 / 0.062 | same prompt, OpenAI-compatible endpoint, 100 tokens, temp 0 | 70B and 120B cannot run; 24B and 27B cannot either | Already rescored their released predictions on the 592; report that table as the replication anchor (done) |
| A3 | Multi Wiki QA da EM (WikiQA column) | Mimir 66.8; Gemma 4 E2B 44.1 (59.3 think); Qwen 3.5 4B 57.1; Qwen 3.5 2B 49.4; Gemma 3 1B 42.6; Qwen 3.5 0.8B 41.6; HRM-Text 34.9; OLMo 2 1B 8.4; SmolLM3 0.3; Munin 49.9 / 48.4 / 55.7 | dfm-evals `multi_wiki_qa`: source `oliverkinch/multi-wiki-qa-high-quality-subset` config `da` (4,767 rows), filter context 30 to 5000 chars and question 10 to 150 chars, mini split seeded 4242 (val 256, test 2048, train 1024), prompt "Tekst: {context}\n\nBesvar følgende spørgsmål om teksten ovenfor med maks. 3 ord.\n\nSpørgsmål: {question}", max_tokens 32, greedy, SQuAD normaliser (casefold, strip punctuation, strip a/an/the), EM and F1 with stderr | Yes. 2048 rows x ~1,000 to 1,500 prompt tokens: Llama 1B under an hour, Gemma 4B a few hours, Mimir ~6 h of prompt processing on the causal-only port | Run all five models with their task code verbatim; this is our "reading fidelity" measured their way and it separates "cannot read Danish" from "cannot find the fact" |
| A4 | PIQA-da accuracy | Mimir 53.7; Gemma 3 1B 72.2; OLMo 2 1B 75.0; Qwen 3.5 0.8B 56.5; Qwen 3.5 4B 70.4 | dfm-evals `piqa` with the bundled `piqa/piqa-dan.json`, Danish prompt "Svar kun med A eller B.", max_tokens 1 (MCQ), letter extraction, accuracy | Yes, minutes | Cheap sanity row that Mimir underperforms on; shows we ran their whole Danish suite, not only Daisy |
| A5 | DaLA macro-F1 (0-shot) | Mimir 96.1; Gemma 3 1B 41.0; Qwen 3.5 0.8B 51.0; Gemma 4 E2B 56.7 | dfm-evals `dala`: `giannor/dala` test (2048 sentences), ja/nej, 8 tokens, greedy, macro-F1 and MCC | Yes, minutes | Optional; a row where Mimir is strongest, useful to show our Mimir port is not broken (if we get ~96, the port is fine on classification and the Daisy gap is about generation) |
| A6 | GEC-DaLA EM | Mimir 85.6; Qwen 3.5 4B 42.6; Gemma 3 1B 3.3 | dfm-evals `gec_dala`: `giannor/dala_gen_v3` config gec_dala, 128 tokens, **temperature 0.1**, EM on stripped strings | Yes, under an hour per model except Mimir (~2 h) | Same port-sanity purpose as A5 but generative; note their 0.1 temperature |
| A7 | Hellaswag-da accuracy | Mimir 35.3; SmolLM3 40.1; Gemma 3 1B 24.8 | EuroEval mini set, 0-shot, MCQ max_tokens 1 | Yes | Low value; skip unless time |
| A8 | IFEval-da accuracy | Mimir 63.9; Gemma 3 1B 47.2; Qwen 3.5 4B 73.7 | dfm-evals `ifeval-da`, max_tokens 2048 (3072 in the suite), strict and loose prompt and instruction accuracy | Marginal for Mimir (hours of 4 tok/s generation); fine for others | Skip for Mimir; optional for the rest |
| A9 | Angry Tweets acc, WMT24++ EN-DA chrF, Nordjylland News chrF | Mimir 67.4 / 53.9 / 35.87 | Angry Tweets task code is not in the public dfm-evals tree (prompt unknown); WMT and summarisation use `wmt24pp` (512 tokens) and a chrF scorer | Slow, off-topic | Skip; list as not reproducible (Angry Tweets) or off-topic |
| A10 | EuroEval Danish leaderboard, Reading comprehension = MultiWikiQA-da, F1 / EM, 4-shot, 32 tokens, 10 bootstrap runs | gemma-3-4b-it 70.94 / 46.06; gemma-3-4b-pt 75.26 / 58.37; Llama-3.2-3B-Instruct 70.23 / 52.62; Llama-3.2-1B 52.21 / 37.62; Llama-3.2-1B-Instruct 8.63 / 0.00; gemma-3-1b-it 17.01 / 0.00; gemma-3-1b-pt 56.45 / 42.20; Qwen2.5-3B-Instruct and DFM-Mimir absent | EuroEval CLI (`euroeval --model ... --dataset multi-wiki-qa-da`), transformers or vLLM backend, versions 16.9 to 17.1 | Feasible with the transformers backend for 1B models; 3B and 4B need many hours (10 x 2048 generations) | Optional; the 0-shot A3 run is the closer match to Mimir's 66.8. Note Llama-3.2-1B-Instruct scores 0.00 EM few-shot: the instruct model ignores the "3 words" format, a format-failure story we already see |
| A11 | EuroEval Danish knowledge (Danske Talemåder, Danish Citizen Tests; MCC / acc, 5-shot) | gemma-3-4b-it 52.57 / 63.91 and 56.53 / 70.72; Llama-3.2-1B-Instruct -0.49 / 23.54 and 0.93 / 35.35; gemma-3-1b-it 1.40 / 22.76 and 15.95 / 43.98 | EuroEval KNOW task, logprob-scored letters | Feasible | Optional "Danish knowledge without retrieval" control for the multilingual models; dfm-evals also has 0-shot `danish-citizen-tests` (test 512, 8 tokens) and `generative-talemaader` (judge-scored) |
| A12 | GSM8K test 1,320, Prolog tool | Qwen2.5-3B GRPO 80.21% (multiple-try N=20, temp 0.2); DeepSeekMath-7B-RL 86.7 | their checkpoints `niklasm222/Qwen2.5-3B-Instruct-GRPO-2K-gsm8k-prolog` (and a Llama 3.2 1B GRPO variant), SWI-Prolog executor, prompts from Appendix A | 3B fp16 does not fit; Q8 GGUF conversion fits; single-try feasible, multiple-try x20 is heavy | Side quest for the letter only: shows we can run their tool loop end to end; not for the page |
| A13 | SommBench Danish WTQA (128 MCQ) | qwen2.5:3b 0.48 (all languages); llama3.1:8b DA 0.61; gpt-5 DA 0.98 | zero-shot, single letter, temp 0 | Feasible if the data is released (no HF link found) | Skip unless the dataset surfaces |
| A14 | BFCL-v1-da tool calling | No small-model number; Munin 8B originals 52.40 to 79.40 acc | dfm-evals `bfcl-v1-da` (Danish exec_simple translations), Inspect tool-call parsing, 1024 tokens | Feasible for models with native tool templates (Gemma 3, Qwen 2.5, Llama 3.2, Mimir) | Strong candidate: a Danish function-calling number for our five models with their code; there is no published small-model row, so it is new rather than a replication |

Standard errors they would expect: Inspect reports `stderr()` per metric. For Daisy on 592, SE at p=0.096 is 1.2 points
(binomial); our 5.6 is 3.3 SE below 9.6, so sampling noise alone does not explain the gap.

---

## 3. Their evaluation harness and settings

### 3.1 The three harnesses they actually use

1. **Inspect AI (AI Security Institute) via `dfm-evals`** (github.com/danish-foundation-models/dfm-evals, fork at
   schneiderkamplab/dfm-evals, last push 26 Aug 2026). Used for the Mimir report and the Munin 1.0 release. Facts:
   - Local Danish tasks: `daisy`, `multi_wiki_qa`, `dala`, `gec_dala`, `piqa` (bundled Danish JSON), `ifeval-da`,
     `danish-citizen-tests`, `generative-talemaader` (LLM judge, Danish judge prompt), `bfcl-v1-da`, `wmt24pp-en-da`,
     plus `ruler` long-context and code tasks via Modal sandboxes; upstream `inspect_evals` for GSM8K, IFEval,
     TruthfulQA, MMLU, ARC, HellaSwag, BFCL, HumanEval, MBPP, AgentHarm, AgentDojo.
   - Suite defaults (`eval-sets.yaml`): `--temperature 0`, `--sample-shuffle 4242`; the `fundamentals` suite caps
     at `--limit 250` per task, the `final_*` suites have no cap; `multi_wiki_qa` at `max_gen_toks=32`; GSM8K 2048
     tokens; IFEval 3072; TruthfulQA 512; BFCL 1024 tokens and message limit 24. The Mimir report says "full
     datasets", so the Danish runs were not the 250-capped suite.
   - Every generative task's `input` is a plain string, which Inspect sends as a single user message through the
     model's chat template; no system prompt is set in any Danish task file.
   - Models are served by vLLM (`vllm_serve.py`, with patches for Qwen 3.5 text-only and an Apertus tool parser) or
     transformers; the report says the Mimir numbers are from transformers.
   - Scoring is per-sample with `mean()` and `stderr()`; exports go to the "Every Eval Ever" format (`eee_export.py`).
   - The `daisy` task (verbatim in `dfm_evals/tasks/daisy.py`): dataset `schneiderkamplab/SDU-Daisy`, split `train`,
     fields Question and Answer, Subject kept as metadata, template = the DAISY Appendix B prompt ending in
     "Spørgsmål: {question}\nSvar:", `generate(max_tokens=100, temperature=0.0)`, prediction stripped and newlines
     replaced by spaces, `normalize_text = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()` (docstring: "Mirror the
     upstream DAISY normalization, including ASCII-only filtering"), EM, token F1 and a hand-written BLEU that
     reproduces NLTK method4 smoothing, max over references.
   - The `multi_wiki_qa` task normaliser differs from Daisy's: `casefold`, strip `string.punctuation`, strip English
     articles, collapse whitespace; Danish letters are kept.
2. **EuroEval** (formerly ScandEval; Dan Saattrup Nielsen, Alexandra Institute, DFM partner). Used in DaLA, Dynaword,
   Encoder vs Decoder, the Munin 1.0 result tables and the public leaderboard. Generative models are prompted
   few-shot (RC 4 shots, knowledge and common sense 5, sentiment and LA 12, NER 8), 10 bootstrap iterations with
   resampled shots, scores reported as mean +- 95% CI; RC metrics F1 and EM (SQuAD normalisation), max 32 generated
   tokens; MCQ tasks are logprob-scored. The Danish RC instruction prompt is the same string dfm-evals uses 0-shot.
   dfm-evals has `lumi/run_euroeval.sbatch` and a custom `dala` dataset config, so they run EuroEval on LUMI too.
3. **The DAISY paper's own runner** (`evaluation/eval.py` in SDU-Daisy): async OpenAI-compatible chat completions,
   `messages=[{"role": "user", "content": PROMPT}]`, `max_tokens=100`, `temperature=0.0`, predictions written to CSV
   with `;` delimiter, scored offline. This is what produced the five big-model prediction files we rescored.

Other tooling they publish: `JustEval` (lm-eval-harness backend, generation separated from scoring), `judging-judges`
(when is an LLM judge good for Danish, work in progress), `aimrun` and `mltiming` for tracking.

### 3.2 Why our Mimir closed-book EM (5.6 on 592) is below their 9.6, ranked by evidence

1. **Attention mode.** Mimir is a prefix-LM (`prefix_lm: true`). In transformers (`modeling_hrm_text.py`) the prompt
   becomes one bidirectional block only when `token_type_ids == 1` is passed for those positions at the first forward
   ("Tokens with token_type_ids == 1 form a single bidirectional block; all other positions are causal"); flash
   attention is refused for prefix-LM ("FlashAttention cannot represent the PrefixLM 4-D mask overlay. Use sdpa
   (default) or flex_attention"). The llama.cpp PR (#27625, noctrex, still open, awaiting three code owners) says
   "causal attention only - the upstream prefix-LM mode is not implemented (the prefix_lm GGUF key round-trips
   unused)". So our Mimir read every prompt causally. Whether their own 9.6 used the bidirectional prefix is itself
   unclear: the report says Mimir "requires FlashAttention to correctly capture the PrefixLM", which contradicts the
   transformers code, and Inspect's transformers provider does not obviously pass `token_type_ids`. Test: run the
   592 in transformers with `token_type_ids` set to 1 over the rendered prompt and again without; the difference is
   the prefix-LM effect and one of the two numbers should land near 9.6.
2. **Quantisation and KV cache.** PR self-test: q8_0 keeps 95.8% top-1 agreement with the bf16 reference; our server
   also ran with `-ctk q8_0 -ctv q8_0` (quantised KV cache) and flash attention on. A 4% per-token flip rate over
   short answers can move a few percent of EM. Test: rerun Mimir closed-book with f16 KV cache and the BF16 GGUF.
3. **Chat template rendering.** Their prompt goes through the Gemma-4 style template
   (`<bos><|turn>user\n{prompt}<turn|>\n<|turn>model\n`; a system turn is emitted only for a system message, tools,
   or `enable_thinking`). With `--jinja` llama.cpp uses the template embedded in the GGUF; verify byte equality of the
   rendered prompt against `apply_chat_template(add_generation_prompt=True)` from the HF repo.
4. **max_tokens.** Theirs is 100; ours should match (the plan says answers were short and untruncated).
5. **Dataset identity.** Same 592 rows (Section 0, fact 1). If the lead's "741" came from the DAISY paper, note that
   the Mimir report used the HF release; the extra 149 questions have no public gold.
6. **Sampling noise.** SE 1.2 points; not sufficient alone.

Their Daisy normaliser also explains some of our "near misses": with `[^a-z0-9]` filtering, "Søren Kierkegaard"
becomes "s ren kierkegaard" on both sides, so EM survives, but "Gyldendal" vs "Forlaget Gyldendal" does not.

### 3.3 Settings summary table (what to state in our model card to match theirs)

| Item | Mimir report / dfm-evals | DAISY paper runner | EuroEval |
|---|---|---|---|
| Shots (Danish) | 0 | 0 | 4 (RC), 5 (MCQ), 12 (LA, sentiment) |
| Decoding | greedy, temp 0 (gec_dala 0.1) | temp 0 | greedy, structured generation |
| Max new tokens | Daisy 100, WikiQA 32, MCQ 1, generation 2048 | 100 | RC 32 |
| Prompt placement | single user message, chat template, no system prompt | single user message | prefix + few-shot block + instruction |
| Daisy normaliser | lower, keep `[a-z0-9]`, no article removal | same | not applicable |
| RC normaliser | casefold, strip punctuation, strip a/an/the | not applicable | SQuAD |
| Aggregation | mean and stderr per metric | mean | 10 bootstrap runs, 95% CI |
| Seed | sample shuffle 4242 | none | per-run |
| Serving | vLLM (FlashInfer) or transformers; Mimir reported from transformers | OpenAI-compatible API | transformers or vLLM |

---

## 4. Ideas for our study, from their own methods (ranked by value per hour on the 1060)

1. **Test the prefix-LM mechanism before publishing any Mimir number (2 to 4 h).** Section 3.2 item 1. The result is
   worth a sentence either way: "Mimir's Daisy score depends on bidirectional prompt attention by X points" or
   "it does not, and the port is fine". Run the same A/B on the retrieve condition: if reading a snippet is where
   bidirectional attention matters, the tool gain for Mimir is currently understated.
2. **Run Multi Wiki QA da with their task code (A3, one evening).** Their 66.8 for Mimir and 42.6 for Gemma 3 1B
   are exactly "can a small model read Danish text and copy the span". Our reading-fidelity numbers (Mimir 0.59,
   Gemma 4B 0.73, Llama 1B 0.37 EM when the answer is present) become comparable to a published column, and the
   two together separate reading failure from retrieval failure.
3. **Give Mimir its native tool interface (half a day).** The chat template renders tool definitions and tool calls
   in Gemma-4 syntax, 9.46% of Mimir's post-training tokens are agentic and tool-use data, and the group's
   `mathagentic` repo builds SFT rows "rendered into Mimir's native tool format". Our agentic condition asked for a
   free-form `SEARCH:` line and Mimir called 0 of 592 times. Passing `tools=[search_da_wikipedia]` through
   `apply_chat_template` and parsing the native call is the fair test of whether Mimir decides to look things up.
   Also run `bfcl-v1-da` (A14) as the published-style function-calling control.
4. **Report the call decision as capability vs propensity (one hour of writing).** Their memorisation paper defines
   PM = 1/2 (1 + (f_p - f_c)/(f_p + f_c)) between an ordinary-use setting and a forcing setting. Our free-form agentic
   run is the propensity setting and the decide-then-search scaffold is the capability setting; Mimir 0 vs 182 calls
   and Llama 1B 0 vs 592 fit that vocabulary exactly.
5. **Add calibration the way Torrielli et al. measure it (2 to 3 h, needs logprobs from llama-server).** ECE with 10
   equal-width bins, Brier, AUROC of "confidence predicts EM", plus a selective-prediction curve (EM at coverage) using
   (M1) answer log-probability and (M2) bootstrap agreement over k samples (they show k=10 gives 70% of the value of
   k=20; we already have 5-sample self-consistency runs, so the agreement rate is free). Then ask whether confidence
   predicts the model's own call decision. This is the missing evaluation dimension they care about most.
6. **Judge-based lenient scoring with a human agreement check (2 h).** PsychoSafe and `generative-talemaader` use an
   LLM judge and report kappa against a human on ~50 items before trusting it. Use Gemma 3 4B as an "is this the same
   answer" judge over our strict-EM misses, Bo labels 50, report kappa, then give judge-EM beside strict and lenient
   EM. It quantifies the format-vs-knowledge split the DAISY paper only illustrates.
7. **Cost accounting in their units (1 h).** Guarded-routing latency definition (mean single-request time over the
   test split, warm start, one in flight), tokens per question per condition, and the Energy Society price
   C = k T sqrt(S) so a 1B and a 4B model are comparable. Report retrieval gain per extra prompt token.
8. **Failure taxonomy with counts (already planned; 2 h).** Their DAISY paper has anecdotes only; their SommBench and
   Moltbook papers count biases (positivity, default answers). Our default-answer table ("carl nielsen" x27) is the
   right shape; add wrong-year offsets and copied-title errors with counts per condition.
9. **Prompt-sensitivity row (1 h).** DAISY's limitation section says the prompt is "version 1" and may not suit all
   models. Two alternative templates on the closed-book condition, report the spread, cite that sentence.
10. **A learned call decision, their way, in miniature (one day; letter material).** Their teaching repo
    BADM500Toolcalling SFTs Gemma 3 270M to emit `<tool_call>search_web(query='...')</tool_call>` with completion-only
    loss (lr 2e-4, batch 2 x 4 accumulation, 30 epochs). Train the same on our logged rows with the 2x2 as labels
    (call iff closed-book was wrong), hold out by Subject, report call precision and recall. GRPO as in the Prolog
    paper (4-bit 3B + LoRA) needed a 40 GB card; on 6 GB it is only realistic for a 0.5B to 1B model with 4-bit LoRA,
    group size 4 and 64-token completions, so name GRPO as the next step and ship the SFT.
11. **Per-Subject and per-answer-type plots (done in data, 1 h to present).** Their model card ships
    `subject_avg_scores.png`; mirror it.
12. **Stderr on every number (30 min).** Inspect prints mean and stderr; EuroEval prints CIs. Add binomial SE to our
    EM columns and bootstrap CIs to the differences between conditions.

Evaluation dimensions they publish that we have not measured: per-metric stderr or CI; a reading-with-context task
(Multi Wiki QA); function-calling accuracy (BFCL-da); calibration (ECE, Brier, AUROC, selective prediction);
judge agreement with humans (kappa); latency and token cost per query; thinking vs non-thinking mode (their
Gemma 4 rows); prompt-variant sensitivity; propensity vs capability.

---

## 5. Open questions

1. Did the Mimir report's Daisy 9.6 use bidirectional prefix attention? The report's FlashAttention sentence and the
   transformers code disagree, and no Inspect provider passes `token_type_ids` by default. Only an A/B run answers it.
2. Is the Mimir HF checkpoint (last modified 20 Aug 2026, 1,750,000 steps on the card vs 1.65M in the report) the
   exact model behind Table 9? The card's numbers match Table 9, so assume yes.
3. Does the GGUF-embedded chat template equal `chat_template.jinja` on the HF repo (Gemma-4 turn markers)? Needs a
   byte diff of one rendered prompt.
4. What is in the 149 Daisy questions withheld from the HF release (741 or 746 minus 592), and were they used in
   the Mimir run? Evidence says no (HF split only), but only the authors can confirm.
5. Which prompt did they use for Angry Tweets (task file not public), and which EuroEval version for Hellaswag-da?
6. Are the Prolog GRPO adapters for Llama 3.2 1B (`niklasm222/llama-3.2-1b-it-GRPO-gsm8k-prolog`) documented
   anywhere? The HF listing exists; no card content was fetched.
7. Is SommBench data public? No dataset link was found.
8. Is `oliverkinch/multi-wiki-qa-high-quality-subset` config `da` what the paper's "oliverkinch/multi-wiki-qa" in
   Table 11 refers to? The dfm-evals code points at the high-quality subset; the report cites the shorter id.
9. The EuroEval leaderboard shows Llama-3.2-3B-Instruct with RC and summarisation only (other columns pending);
   Qwen2.5-3B-Instruct is absent. If we want an EuroEval column for those two we must produce it ourselves.

---

## Appendix A. Public assets by the group (as of 4 Sep 2026)

- Models (HF danish-foundation-models): DFM-Mimir (1B HRM, Apache 2.0, 7,316 downloads), munin-apertus-8b,
  munin-ministral3-8B, munin-qwen3.5-9B, munin-gemma4-e4b, munin-dfm-7B, dfm-decoder-open-v0-7b-pt, munin-7b-alpha
  (2023), six gemma-3-1b Dynaword ablations, a croco-munin-apertus-8b DPO/SimPO series. GGUF of Mimir by noctrex
  (community), needs llama.cpp PR #27625.
- Datasets (HF): schneiderkamplab/SDU-Daisy (592), danish-dynaword and the Norwegian, Swedish, Icelandic, Faroese,
  Dutch dynawords, dala family, ifeval-da, multi-ifeval, kaenguruen, global-piqa-da, laerebogen, ai-arenaen,
  multilingual-gsm-symbolic, danish-wildchat4.8M, synthetic-values-model-charter, dfm-dyna-instruct;
  niklasm222/gsm8k-prolog-prover.
- Code (GitHub): schneiderkamplab/SDU-Daisy, dfm-evals (fork of danish-foundation-models/dfm-evals), JustEval,
  HRM-Text (fork), data_io, mathagentic, fineinstructions, BADM500Toolcalling, FlexMoRE, DeToNATION, bitlinear,
  brainsurgery, MiniMoE (tokcleanse), offpolicy_kd, sensai (teacher logits for distillation), mldataforge,
  synthesizers, syntheval; lgalke/multilingual-gsm-symbolic, gqr, Culture_Neurons, logit-diff-lens,
  language-steering, shutdown_avoidance, EGG; aisilab/Prolog-as-a-Tool; danish-foundation-models/prime-rl (async RL
  at scale, Aug 2026), judging-judges, model-charter, dfm-sdg.
- Sites: foundationmodels.dk (Mimir release note 14 Aug 2026; Munin 1.0 full results page), euroeval.com.

## Appendix B. Where each number in this file came from

Mimir: arXiv html 2608.13517v2 Tables 6 to 13 and Section 5; HF model card and config.json; transformers
`modeling_hrm_text.py`; llama.cpp PR 27625 description. DAISY: arXiv html 2601.19930 Sections 3 to 7, Appendix B;
SDU-Daisy README and evaluation/eval.py; HF dataset card and commit list. dfm-evals: raw files from
github.com/danish-foundation-models/dfm-evals main (daisy.py, multi_wiki_qa.py, dala.py, gec_dala.py, piqa.py,
danish_citizen_tests.py, talemaader, eval-sets.yaml, README, tests/test_daisy.py). EuroEval: src/euroeval/tasks.py,
prompt_templates/reading_comprehension.py, dataset_configs/danish.py, leaderboards/danish_all.csv. Prolog:
arXiv html 2512.07407v3 Tables 1 to 6, Appendices A to D; HF niklasm222 listing. Others: arXiv html of each id.
