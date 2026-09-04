# DAISY with tools: results

## Replication: the group's own predictions, rescored on the 592 public golds

| model | n | EM | F1 | BLEU | paper F1 | paper BLEU |
|---|---|---|---|---|---|---|
| meta-llama-Llama-3.3-70B-Instruct | 592 | 0.225 | 0.277 | 0.172 | 0.268 | 0.166 |
| openai-gpt-oss-120b | 592 | 0.171 | 0.218 | 0.131 | 0.211 | 0.126 |
| mistralai-Mistral-Small-3.1-24B-Instruct-2503 | 592 | 0.169 | 0.217 | 0.134 | 0.202 | 0.124 |
| google-gemma-3-27b-it | 592 | 0.171 | 0.203 | 0.132 | 0.193 | 0.123 |
| openai-gpt-oss-20b | 592 | 0.074 | 0.110 | 0.064 | 0.112 | 0.062 |

## Retrieval ceiling: gold answer literally inside the top-3 Danish Wikipedia intros

| query formulation | n | hit rate |
|---|---|---|
| question (retrieval_ceiling_k3.jsonl) | 360 | 0.228 |
| subject (retrieval_ceiling_k3.jsonl) | 360 | 0.803 |
| question (retrieval_ceiling_k3_question-subject.jsonl) | 592 | 0.215 |
| subject (retrieval_ceiling_k3_question-subject.jsonl) | 592 | 0.787 |
| shaped (retrieval_ceiling_k3_shaped-subject_en.jsonl) | 116 | 0.155 |
| subject (retrieval_ceiling_k3_shaped-subject_en.jsonl) | 116 | 0.284 |
| shaped (retrieval_ceiling_k3_shaped.jsonl) | 592 | 0.404 |

## Our runs: small models, greedy, zero-shot, the group's prompt and scorer

| model | condition | n | EM | lenient EM | F1 | BLEU | tool calls | fallback | s/row |
|---|---|---|---|---|---|---|---|---|---|
| gemma4b | agentic-fewshot | 592 | 0.397 | 0.417 | 0.436 | 0.287 | 445 | 51 | 5.2 |
| gemma4b | agentic-scaffold | 592 | 0.289 | 0.297 | 0.318 | 0.208 | 523 | 0 | 4.7 |
| gemma4b | agentic | 592 | 0.399 | 0.426 | 0.443 | 0.285 | 553 | 77 | 5.9 |
| gemma4b | closed-sc | 592 | 0.054 | 0.062 | 0.079 | 0.045 | 0 | 0 | 3.3 |
| gemma4b | closed | 592 | 0.056 | 0.062 | 0.083 | 0.047 | 0 | 0 | 1.2 |
| gemma4b | retrieve-oracle | 592 | 0.679 | 0.720 | 0.731 | 0.484 | 592 | 0 | 3.6 |
| gemma4b | retrieve | 592 | 0.311 | 0.323 | 0.340 | 0.219 | 592 | 0 | 3.7 |
| llama1b | agentic-fewshot | 592 | 0.014 | 0.027 | 0.034 | 0.015 | 1 | 0 | 0.2 |
| llama1b | agentic-scaffold | 592 | 0.150 | 0.257 | 0.215 | 0.119 | 592 | 0 | 1.2 |
| llama1b | agentic | 592 | 0.008 | 0.022 | 0.028 | 0.012 | 0 | 0 | 0.2 |
| llama1b | closed-sc | 592 | 0.012 | 0.034 | 0.033 | 0.016 | 0 | 0 | 1.0 |
| llama1b | closed | 592 | 0.008 | 0.029 | 0.031 | 0.012 | 0 | 0 | 0.3 |
| llama1b | retrieve-oracle | 592 | 0.392 | 0.579 | 0.482 | 0.285 | 592 | 0 | 0.9 |
| llama1b | retrieve | 592 | 0.152 | 0.257 | 0.214 | 0.118 | 592 | 0 | 1.3 |
| llama3b | agentic-fewshot | 592 | 0.052 | 0.074 | 0.086 | 0.040 | 13 | 0 | 0.6 |
| llama3b | agentic-scaffold | 592 | 0.066 | 0.078 | 0.088 | 0.057 | 72 | 0 | 1.0 |
| llama3b | agentic | 592 | 0.037 | 0.049 | 0.067 | 0.031 | 0 | 0 | 0.5 |
| llama3b | closed-sc | 592 | 0.039 | 0.042 | 0.058 | 0.032 | 0 | 0 | 1.5 |
| llama3b | closed | 592 | 0.041 | 0.044 | 0.060 | 0.033 | 0 | 0 | 0.4 |
| llama3b | retrieve-oracle | 592 | 0.644 | 0.718 | 0.709 | 0.463 | 592 | 0 | 2.2 |
| llama3b | retrieve | 592 | 0.282 | 0.328 | 0.326 | 0.208 | 592 | 0 | 2.9 |
| mimir-official | closed | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | nan |
| mimir | agentic-fewshot | 592 | 0.030 | 0.059 | 0.063 | 0.030 | 0 | 0 | 7.4 |
| mimir | agentic-scaffold | 592 | 0.120 | 0.152 | 0.163 | 0.096 | 182 | 0 | 8.3 |
| mimir | agentic | 592 | 0.049 | 0.076 | 0.076 | 0.045 | 0 | 0 | 7.1 |
| mimir | closed-sc | 592 | 0.062 | 0.078 | 0.087 | 0.055 | 0 | 0 | 20.2 |
| mimir | closed | 592 | 0.056 | 0.078 | 0.087 | 0.048 | 0 | 0 | 6.0 |
| mimir | retrieve-oracle | 592 | 0.606 | 0.650 | 0.669 | 0.441 | 592 | 0 | 8.5 |
| mimir | retrieve | 592 | 0.265 | 0.301 | 0.316 | 0.202 | 592 | 0 | 9.3 |
| qwen3b | agentic-fewshot | 592 | 0.390 | 0.443 | 0.452 | 0.268 | 588 | 135 | 3.6 |
| qwen3b | agentic-scaffold | 592 | 0.275 | 0.304 | 0.318 | 0.208 | 584 | 0 | 2.9 |
| qwen3b | agentic | 592 | 0.400 | 0.446 | 0.462 | 0.277 | 592 | 155 | 3.7 |
| qwen3b | closed-sc | 592 | 0.032 | 0.037 | 0.051 | 0.031 | 0 | 0 | 1.5 |
| qwen3b | closed | 592 | 0.030 | 0.041 | 0.055 | 0.030 | 0 | 0 | 0.4 |
| qwen3b | retrieve-oracle | 592 | 0.628 | 0.672 | 0.691 | 0.455 | 592 | 0 | 2.2 |
| qwen3b | retrieve | 592 | 0.279 | 0.316 | 0.323 | 0.209 | 592 | 0 | 2.6 |

## By answer type (EM)

| model | condition | year | number | text |
|---|---|---|---|---|
| gemma4b | agentic-fewshot | 0.461 (n=141) | 0.269 (n=52) | 0.391 (n=399) |
| gemma4b | agentic-scaffold | 0.319 (n=141) | 0.269 (n=52) | 0.281 (n=399) |
| gemma4b | agentic | 0.447 (n=141) | 0.385 (n=52) | 0.383 (n=399) |
| gemma4b | closed-sc | 0.021 (n=141) | 0.019 (n=52) | 0.070 (n=399) |
| gemma4b | closed | 0.028 (n=141) | 0.019 (n=52) | 0.070 (n=399) |
| gemma4b | retrieve-oracle | 0.823 (n=141) | 0.481 (n=52) | 0.654 (n=399) |
| gemma4b | retrieve | 0.319 (n=141) | 0.308 (n=52) | 0.308 (n=399) |
| llama1b | agentic-fewshot | 0.007 (n=141) | 0.000 (n=52) | 0.018 (n=399) |
| llama1b | agentic-scaffold | 0.206 (n=141) | 0.135 (n=52) | 0.133 (n=399) |
| llama1b | agentic | 0.007 (n=141) | 0.000 (n=52) | 0.010 (n=399) |
| llama1b | closed-sc | 0.014 (n=141) | 0.019 (n=52) | 0.010 (n=399) |
| llama1b | closed | 0.007 (n=141) | 0.000 (n=52) | 0.010 (n=399) |
| llama1b | retrieve-oracle | 0.504 (n=141) | 0.269 (n=52) | 0.368 (n=399) |
| llama1b | retrieve | 0.213 (n=141) | 0.115 (n=52) | 0.135 (n=399) |
| llama3b | agentic-fewshot | 0.035 (n=141) | 0.019 (n=52) | 0.063 (n=399) |
| llama3b | agentic-scaffold | 0.106 (n=141) | 0.038 (n=52) | 0.055 (n=399) |
| llama3b | agentic | 0.035 (n=141) | 0.000 (n=52) | 0.043 (n=399) |
| llama3b | closed-sc | 0.035 (n=141) | 0.000 (n=52) | 0.045 (n=399) |
| llama3b | closed | 0.050 (n=141) | 0.000 (n=52) | 0.043 (n=399) |
| llama3b | retrieve-oracle | 0.816 (n=141) | 0.423 (n=52) | 0.612 (n=399) |
| llama3b | retrieve | 0.305 (n=141) | 0.231 (n=52) | 0.281 (n=399) |
| mimir-official | closed | - | - | - |
| mimir | agentic-fewshot | 0.057 (n=141) | 0.000 (n=52) | 0.025 (n=399) |
| mimir | agentic-scaffold | 0.121 (n=141) | 0.115 (n=52) | 0.120 (n=399) |
| mimir | agentic | 0.092 (n=141) | 0.000 (n=52) | 0.040 (n=399) |
| mimir | closed-sc | 0.113 (n=141) | 0.000 (n=52) | 0.053 (n=399) |
| mimir | closed | 0.078 (n=141) | 0.000 (n=52) | 0.055 (n=399) |
| mimir | retrieve-oracle | 0.837 (n=141) | 0.365 (n=52) | 0.556 (n=399) |
| mimir | retrieve | 0.348 (n=141) | 0.192 (n=52) | 0.246 (n=399) |
| qwen3b | agentic-fewshot | 0.369 (n=141) | 0.327 (n=52) | 0.406 (n=399) |
| qwen3b | agentic-scaffold | 0.326 (n=141) | 0.212 (n=52) | 0.266 (n=399) |
| qwen3b | agentic | 0.369 (n=141) | 0.269 (n=52) | 0.429 (n=399) |
| qwen3b | closed-sc | 0.043 (n=141) | 0.019 (n=52) | 0.030 (n=399) |
| qwen3b | closed | 0.043 (n=141) | 0.019 (n=52) | 0.028 (n=399) |
| qwen3b | retrieve-oracle | 0.801 (n=141) | 0.462 (n=52) | 0.589 (n=399) |
| qwen3b | retrieve | 0.326 (n=141) | 0.269 (n=52) | 0.263 (n=399) |

## Did the model know when to look? (agentic call decision vs closed-book correctness, EM)

Reading: 'called when wrong' is the useful call, 'silent when wrong' is the bluff, 'called when right' is wasted effort.

| model | agentic variant | called when wrong | silent when wrong | called when right | silent when right | call precision | call recall |
|---|---|---|---|---|---|---|---|
| gemma4b | agentic | 525 | 34 | 28 | 5 | 0.95 | 0.94 |
| gemma4b | agentic-fewshot | 430 | 129 | 15 | 18 | 0.97 | 0.77 |
| gemma4b | agentic-scaffold | 495 | 64 | 28 | 5 | 0.95 | 0.89 |
| llama1b | agentic | 0 | 587 | 0 | 5 | nan | 0.00 |
| llama1b | agentic-fewshot | 1 | 586 | 0 | 5 | 1.00 | 0.00 |
| llama1b | agentic-scaffold | 587 | 0 | 5 | 0 | 0.99 | 1.00 |
| llama3b | agentic | 0 | 568 | 0 | 24 | nan | 0.00 |
| llama3b | agentic-fewshot | 13 | 555 | 0 | 24 | 1.00 | 0.02 |
| llama3b | agentic-scaffold | 69 | 499 | 3 | 21 | 0.96 | 0.12 |
| mimir | agentic | 0 | 559 | 0 | 33 | nan | 0.00 |
| mimir | agentic-fewshot | 0 | 559 | 0 | 33 | nan | 0.00 |
| mimir | agentic-scaffold | 176 | 383 | 6 | 27 | 0.97 | 0.31 |
| qwen3b | agentic | 574 | 0 | 18 | 0 | 0.97 | 1.00 |
| qwen3b | agentic-fewshot | 571 | 3 | 17 | 1 | 0.97 | 0.99 |
| qwen3b | agentic-scaffold | 566 | 8 | 18 | 0 | 0.97 | 0.99 |

## Reading fidelity: EM when the gold answer was inside the retrieved intros vs when it was not (retrieve condition)

| model | EM given answer present | n | EM given answer absent | n |
|---|---|---|---|---|
| gemma4b | 0.728 | 239 | 0.028 | 353 |
| llama1b | 0.368 | 239 | 0.006 | 353 |
| llama3b | 0.665 | 239 | 0.023 | 353 |
| mimir | 0.590 | 239 | 0.045 | 353 |
| qwen3b | 0.644 | 239 | 0.031 | 353 |

## Can the model ask? Model-written queries whose first Wikipedia hit is the question's own subject page

| model | variant | calls | first hit = subject | rate | empty results (fell back) |
|---|---|---|---|---|---|
| gemma4b | agentic-fewshot | 445 | 253 | 0.57 | 51 |
| gemma4b | agentic | 553 | 266 | 0.48 | 77 |
| llama1b | agentic-fewshot | 1 | 0 | 0.00 | 0 |
| llama1b | agentic | 0 | 0 | nan | 0 |
| llama3b | agentic-fewshot | 13 | 7 | 0.54 | 0 |
| llama3b | agentic | 0 | 0 | nan | 0 |
| mimir | agentic-fewshot | 0 | 0 | nan | 0 |
| mimir | agentic | 0 | 0 | nan | 0 |
| qwen3b | agentic-fewshot | 588 | 295 | 0.50 | 135 |
| qwen3b | agentic | 592 | 308 | 0.52 | 155 |

## Default answers: most repeated predictions per run

| model | condition | top repeated predictions (count) | share of rows |
|---|---|---|---|
| gemma4b | agentic-fewshot | ukendt (15); ikke angivet (15); ikke nævnt (13) | 0.07 |
| gemma4b | agentic-scaffold | ukendt (27); ikke nævnt (16); carl nielsen (11) | 0.09 |
| gemma4b | agentic | ikke angivet (23); ikke nævnt (18); carl nielsen (10) | 0.09 |
| gemma4b | closed-sc | carl nielsen (18); kim larsen (13); søren kierkegaard (10) | 0.07 |
| gemma4b | closed | carl nielsen (18); kim larsen (14); søren kierkegaard (9) | 0.07 |
| gemma4b | retrieve-oracle | ikke angivet (13); kai normann andersen (12); ukendt (10) | 0.06 |
| gemma4b | retrieve | ukendt (31); ikke nævnt (21); carl nielsen (10) | 0.10 |
| llama1b | agentic-fewshot | 2014 (22); 2010 (17); 2015 (11) | 0.08 |
| llama1b | agentic-scaffold | carl nielsen (11); niels w gade (8); 1998 (3) | 0.04 |
| llama1b | agentic | 2014 (14); 2010 (12); mogens lindberg (10) | 0.06 |
| llama1b | closed-sc | leonardo da vinci (16); ludwig van beethoven (4); mozart (4) | 0.04 |
| llama1b | closed | leonardo da vinci (14); mogens lindberg (9); 1995 (9) | 0.05 |
| llama1b | retrieve-oracle | kai normann andersen (6); 1838 (5); børge og arvid m ller (5) | 0.03 |
| llama1b | retrieve | carl nielsen (11); niels w gade (8); 1998 (3) | 0.04 |
| llama3b | agentic-fewshot | jørgen leth (11); jørgen madsen (11); jeg er usikker på svaret (11) | 0.06 |
| llama3b | agentic-scaffold | hans christian andersen (22); københavn (9); niels gade (8) | 0.07 |
| llama3b | agentic | hans christian andersen (13); jørgen madsen (10); niels gade (9) | 0.05 |
| llama3b | closed-sc | hans christian andersen (13); københavn (9); søren kierkegaard (8) | 0.05 |
| llama3b | closed | hans christian andersen (24); københavn (9); 1984 (8) | 0.07 |
| llama3b | retrieve-oracle | kai normann andersen (12); 1838 (4); h c lumbye (4) | 0.03 |
| llama3b | retrieve | jeg er ikke klar over spørgs (9); jeg er ukendt (8); carl nielsen (7) | 0.04 |
| mimir-official | closed |  | 0.00 |
| mimir | agentic-fewshot | 2000 (31); søren ulrik thomsen (19); svar carl nielsen (17) | 0.11 |
| mimir | agentic-scaffold | mona lisa (16); hans christian andersen (14); carl nielsen (14) | 0.07 |
| mimir | agentic | carl nielsen (18); mona lisa (17); 2000 (17) | 0.09 |
| mimir | closed-sc | carl nielsen (19); mona lisa (18); h c andersen (17) | 0.09 |
| mimir | closed | carl nielsen (27); hans christian andersen (20); mona lisa (19) | 0.11 |
| mimir | retrieve-oracle | kai normann andersen (11); poul reichhardt (4); 1978 (4) | 0.03 |
| mimir | retrieve | carl nielsen (11); niels w gade (7); 1973 (6) | 0.04 |
| qwen3b | agentic-fewshot | kai normann andersen (8); 1988 (4); carl nielsen (4) | 0.03 |
| qwen3b | agentic-scaffold | carl nielsen (9); c e f weyse (8); poul reichhardt (4) | 0.04 |
| qwen3b | agentic | kai normann andersen (7); carl nielsen (5); børge m ller (4) | 0.03 |
| qwen3b | closed-sc | carl nielsen (18); hans christian andersen (10); 12 (9) | 0.06 |
| qwen3b | closed | carl nielsen (21); 12 (14); 1991 (9) | 0.07 |
| qwen3b | retrieve-oracle | kai normann andersen (12); liva weel (4); 1838 (4) | 0.03 |
| qwen3b | retrieve | c e f weyse (8); carl nielsen (7); poul reichhardt (4) | 0.03 |
