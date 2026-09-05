# DAISY with tools: results

## Replication: the group's own predictions, rescored on the 592 public golds

| model | n | EM | F1 | BLEU | paper F1 | paper BLEU |
|---|---|---|---|---|---|---|
| meta-llama-Llama-3.3-70B-Instruct | 592 | 0.225 | 0.277 | 0.172 | 0.268 | 0.166 |
| openai-gpt-oss-120b | 592 | 0.171 | 0.218 | 0.131 | 0.211 | 0.126 |
| mistralai-Mistral-Small-3.1-24B-Instruct-2503 | 592 | 0.169 | 0.217 | 0.134 | 0.202 | 0.124 |
| google-gemma-3-27b-it | 592 | 0.171 | 0.203 | 0.132 | 0.193 | 0.123 |
| openai-gpt-oss-20b | 592 | 0.074 | 0.110 | 0.064 | 0.112 | 0.062 |

## Answer recall@3 (retrieval ceiling): gold answer literally inside the top-3 Danish Wikipedia intros

| query formulation | n | hit rate |
|---|---|---|
| question (retrieval_ceiling_k3.jsonl) | 360 | 0.228 |
| subject (retrieval_ceiling_k3.jsonl) | 360 | 0.803 |
| question (retrieval_ceiling_k3_question-subject.jsonl) | 592 | 0.215 |
| subject (retrieval_ceiling_k3_question-subject.jsonl) | 592 | 0.787 |
| shaped (retrieval_ceiling_k3_shaped-subject_en.jsonl) | 592 | 0.149 |
| subject (retrieval_ceiling_k3_shaped-subject_en.jsonl) | 592 | 0.282 |
| shaped (retrieval_ceiling_k3_shaped.jsonl) | 592 | 0.404 |

## Our runs: small models, greedy, zero-shot, the group's prompt and scorer

| model | condition | n | EM (SQuAD) | 95% CI | contains-gold acc. | F1 | BLEU | tool calls | fallback | s/row | answer in context | EM given present |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gemma4b | agentic-fewshot | 592 | 0.397 | 0.360 to 0.436 | 0.417 | 0.436 | 0.287 | 445 | 51 | 5.2 | | |
| gemma4b | agentic-local | 592 | 0.485 | 0.443 to 0.522 | 0.530 | 0.544 | 0.369 | 551 | 4 | 6.6 | 0.633 | 0.794 |
| gemma4b | agentic-scaffold | 592 | 0.289 | 0.253 to 0.326 | 0.297 | 0.318 | 0.208 | 523 | 0 | 4.7 | | |
| gemma4b | agentic | 592 | 0.399 | 0.361 to 0.436 | 0.426 | 0.443 | 0.285 | 553 | 77 | 5.9 | | |
| gemma4b | closed-sc | 592 | 0.054 | 0.035 to 0.074 | 0.062 | 0.079 | 0.045 | 0 | 0 | 3.3 | | |
| gemma4b | closed | 592 | 0.056 | 0.037 to 0.074 | 0.062 | 0.083 | 0.047 | 0 | 0 | 1.2 | | |
| gemma4b | retrieve-local | 592 | 0.657 | 0.617 to 0.696 | 0.693 | 0.705 | 0.462 | 592 | 0 | 5.6 | 0.755 | 0.855 |
| gemma4b | retrieve-oracle | 592 | 0.679 | 0.642 to 0.718 | 0.720 | 0.731 | 0.484 | 592 | 0 | 3.6 | | |
| gemma4b | retrieve-plus-local | 592 | 0.688 | 0.650 to 0.725 | 0.731 | 0.744 | 0.490 | 592 | 0 | 8.4 | 0.812 | 0.832 |
| gemma4b | retrieve | 592 | 0.311 | 0.275 to 0.348 | 0.323 | 0.340 | 0.219 | 592 | 0 | 3.7 | | |
| llama1b | agentic-fewshot | 592 | 0.014 | 0.005 to 0.024 | 0.027 | 0.034 | 0.015 | 1 | 0 | 0.2 | | |
| llama1b | agentic-local | 592 | 0.007 | 0.002 to 0.014 | 0.024 | 0.027 | 0.011 | 0 | 0 | 0.2 | | |
| llama1b | agentic-scaffold | 592 | 0.150 | 0.123 to 0.179 | 0.257 | 0.215 | 0.119 | 592 | 0 | 1.2 | | |
| llama1b | agentic | 592 | 0.008 | 0.002 to 0.017 | 0.022 | 0.028 | 0.012 | 0 | 0 | 0.2 | | |
| llama1b | closed-sc | 592 | 0.012 | 0.003 to 0.022 | 0.034 | 0.033 | 0.016 | 0 | 0 | 1.0 | | |
| llama1b | closed | 592 | 0.008 | 0.002 to 0.017 | 0.029 | 0.031 | 0.012 | 0 | 0 | 0.3 | | |
| llama1b | retrieve-given-gemma | 592 | 0.250 | 0.215 to 0.285 | 0.367 | 0.314 | 0.180 | 476 | 116 | 1.1 | | |
| llama1b | retrieve-local | 592 | 0.338 | 0.301 to 0.375 | 0.517 | 0.432 | 0.239 | 592 | 0 | 2.0 | 0.755 | 0.445 |
| llama1b | retrieve-oracle | 592 | 0.392 | 0.353 to 0.431 | 0.579 | 0.482 | 0.285 | 592 | 0 | 0.9 | | |
| llama1b | retrieve-plus-local | 592 | 0.412 | 0.372 to 0.451 | 0.574 | 0.498 | 0.296 | 592 | 0 | 3.4 | 0.812 | 0.507 |
| llama1b | retrieve | 592 | 0.152 | 0.125 to 0.181 | 0.257 | 0.214 | 0.118 | 592 | 0 | 1.3 | | |
| llama3b | agentic-fewshot | 592 | 0.052 | 0.035 to 0.071 | 0.074 | 0.086 | 0.040 | 13 | 0 | 0.6 | | |
| llama3b | agentic-local | 592 | 0.037 | 0.022 to 0.054 | 0.049 | 0.066 | 0.031 | 0 | 0 | 0.5 | | |
| llama3b | agentic-scaffold | 592 | 0.066 | 0.047 to 0.086 | 0.078 | 0.088 | 0.057 | 72 | 0 | 1.0 | | |
| llama3b | agentic | 592 | 0.037 | 0.022 to 0.054 | 0.049 | 0.067 | 0.031 | 0 | 0 | 0.5 | | |
| llama3b | closed-sc | 592 | 0.039 | 0.025 to 0.056 | 0.042 | 0.058 | 0.032 | 0 | 0 | 1.5 | | |
| llama3b | closed | 592 | 0.041 | 0.025 to 0.057 | 0.044 | 0.060 | 0.033 | 0 | 0 | 0.4 | | |
| llama3b | retrieve-local | 592 | 0.613 | 0.573 to 0.654 | 0.689 | 0.679 | 0.437 | 592 | 0 | 4.4 | 0.755 | 0.794 |
| llama3b | retrieve-oracle | 592 | 0.644 | 0.606 to 0.681 | 0.718 | 0.709 | 0.463 | 592 | 0 | 2.2 | | |
| llama3b | retrieve-plus-local | 592 | 0.644 | 0.605 to 0.682 | 0.736 | 0.724 | 0.461 | 592 | 0 | 6.8 | 0.812 | 0.780 |
| llama3b | retrieve | 592 | 0.282 | 0.247 to 0.318 | 0.328 | 0.326 | 0.208 | 592 | 0 | 2.9 | | |
| mimir-hf | agentic-local | 592 | 0.120 | 0.095 to 0.147 | 0.132 | 0.139 | 0.093 | 56 | 0 | 9.6 | 0.732 | 0.829 |
| mimir-hf | agentic-scaffold | 592 | 0.123 | 0.098 to 0.150 | 0.137 | 0.154 | 0.111 | 94 | 0 | 4.2 | | |
| mimir-hf | agentic | 592 | 0.123 | 0.096 to 0.150 | 0.139 | 0.145 | 0.096 | 56 | 1 | 3.3 | | |
| mimir-hf | closed | 592 | 0.084 | 0.062 to 0.108 | 0.096 | 0.115 | 0.076 | 0 | 0 | 1.9 | | |
| mimir-hf | retrieve-given-gemma+qwen | 592 | 0.534 | 0.495 to 0.574 | 0.579 | 0.596 | 0.375 | 543 | 49 | 12.3 | 0.619 | 0.841 |
| mimir-hf | retrieve-given-qwen | 592 | 0.473 | 0.434 to 0.514 | 0.503 | 0.525 | 0.328 | 437 | 155 | 8.3 | | |
| mimir-hf | retrieve-local | 592 | 0.659 | 0.620 to 0.698 | 0.703 | 0.715 | 0.469 | 592 | 0 | 26.2 | 0.755 | 0.861 |
| mimir-hf | retrieve-oracle | 592 | 0.694 | 0.660 to 0.730 | 0.736 | 0.748 | 0.498 | 592 | 0 | 8.6 | | |
| mimir-hf | retrieve-plus-local | 592 | 0.716 | 0.681 to 0.758 | 0.757 | 0.772 | 0.508 | 592 | 0 | 43.5 | 0.812 | 0.871 |
| mimir-hf | retrieve-plus-qwenq-local | 1 | 1.000 | 1.000 to 1.000 | 1.000 | 1.000 | 1.000 | 1 | 0 | 79.1 | 1.000 | 1.000 |
| mimir-hf | retrieve | 592 | 0.326 | 0.289 to 0.365 | 0.351 | 0.365 | 0.237 | 592 | 0 | 8.1 | | |
| mimir-official-prefix-t100 | closed | 592 | 0.084 | 0.061 to 0.108 | 0.096 | 0.115 | 0.077 | 0 | 0 | 576.7 | | |
| mimir-official-t100 | closed | 592 | 0.054 | 0.037 to 0.073 | 0.079 | 0.081 | 0.049 | 0 | 0 | 593.5 | | |
| mimir-official | closed | 0 | 0.000 | nan to nan | 0.000 | 0.000 | 0.000 | 0 | 0 | nan | | |
| mimir | agentic-fewshot | 592 | 0.030 | 0.019 to 0.044 | 0.059 | 0.063 | 0.030 | 0 | 0 | 7.4 | | |
| mimir | agentic-scaffold | 592 | 0.120 | 0.095 to 0.147 | 0.152 | 0.163 | 0.096 | 182 | 0 | 8.3 | | |
| mimir | agentic | 592 | 0.049 | 0.032 to 0.068 | 0.076 | 0.076 | 0.045 | 0 | 0 | 7.1 | | |
| mimir | closed-sc | 592 | 0.062 | 0.042 to 0.083 | 0.078 | 0.087 | 0.055 | 0 | 0 | 20.2 | | |
| mimir | closed | 592 | 0.056 | 0.037 to 0.074 | 0.078 | 0.087 | 0.048 | 0 | 0 | 6.0 | | |
| mimir | retrieve-given-gemma | 592 | 0.365 | 0.328 to 0.402 | 0.402 | 0.415 | 0.263 | 476 | 116 | 9.1 | | |
| mimir | retrieve-given-qwen | 592 | 0.382 | 0.345 to 0.422 | 0.427 | 0.446 | 0.267 | 437 | 155 | 9.3 | | |
| mimir | retrieve-oracle | 592 | 0.606 | 0.571 to 0.645 | 0.650 | 0.669 | 0.441 | 592 | 0 | 8.5 | | |
| mimir | retrieve | 592 | 0.265 | 0.233 to 0.299 | 0.301 | 0.316 | 0.202 | 592 | 0 | 9.3 | | |
| qwen3b | agentic-fewshot | 592 | 0.390 | 0.351 to 0.427 | 0.443 | 0.452 | 0.268 | 588 | 135 | 3.6 | | |
| qwen3b | agentic-local | 592 | 0.554 | 0.514 to 0.595 | 0.601 | 0.616 | 0.395 | 592 | 2 | 4.5 | 0.726 | 0.747 |
| qwen3b | agentic-scaffold | 592 | 0.275 | 0.242 to 0.312 | 0.304 | 0.318 | 0.208 | 584 | 0 | 2.9 | | |
| qwen3b | agentic | 592 | 0.400 | 0.363 to 0.436 | 0.446 | 0.462 | 0.277 | 592 | 155 | 3.7 | | |
| qwen3b | closed-sc | 592 | 0.032 | 0.019 to 0.047 | 0.037 | 0.051 | 0.031 | 0 | 0 | 1.5 | | |
| qwen3b | closed | 592 | 0.030 | 0.017 to 0.044 | 0.041 | 0.055 | 0.030 | 0 | 0 | 0.4 | | |
| qwen3b | retrieve-local | 592 | 0.598 | 0.559 to 0.637 | 0.639 | 0.662 | 0.432 | 592 | 0 | 4.2 | 0.755 | 0.776 |
| qwen3b | retrieve-oracle | 592 | 0.628 | 0.591 to 0.666 | 0.672 | 0.691 | 0.455 | 592 | 0 | 2.2 | | |
| qwen3b | retrieve-plus-local | 592 | 0.639 | 0.598 to 0.677 | 0.681 | 0.706 | 0.459 | 592 | 0 | 6.4 | 0.812 | 0.778 |
| qwen3b | retrieve | 592 | 0.279 | 0.245 to 0.318 | 0.316 | 0.323 | 0.209 | 592 | 0 | 2.6 | | |

## By answer type (EM)

| model | condition | year | number | text |
|---|---|---|---|---|
| gemma4b | agentic-fewshot | 0.461 (n=141) | 0.269 (n=52) | 0.391 (n=399) |
| gemma4b | agentic-local | 0.695 (n=141) | 0.385 (n=52) | 0.424 (n=399) |
| gemma4b | agentic-scaffold | 0.319 (n=141) | 0.269 (n=52) | 0.281 (n=399) |
| gemma4b | agentic | 0.447 (n=141) | 0.385 (n=52) | 0.383 (n=399) |
| gemma4b | closed-sc | 0.021 (n=141) | 0.019 (n=52) | 0.070 (n=399) |
| gemma4b | closed | 0.028 (n=141) | 0.019 (n=52) | 0.070 (n=399) |
| gemma4b | retrieve-local | 0.816 (n=141) | 0.500 (n=52) | 0.622 (n=399) |
| gemma4b | retrieve-oracle | 0.823 (n=141) | 0.481 (n=52) | 0.654 (n=399) |
| gemma4b | retrieve-plus-local | 0.844 (n=141) | 0.519 (n=52) | 0.654 (n=399) |
| gemma4b | retrieve | 0.319 (n=141) | 0.308 (n=52) | 0.308 (n=399) |
| llama1b | agentic-fewshot | 0.007 (n=141) | 0.000 (n=52) | 0.018 (n=399) |
| llama1b | agentic-local | 0.007 (n=141) | 0.000 (n=52) | 0.008 (n=399) |
| llama1b | agentic-scaffold | 0.206 (n=141) | 0.135 (n=52) | 0.133 (n=399) |
| llama1b | agentic | 0.007 (n=141) | 0.000 (n=52) | 0.010 (n=399) |
| llama1b | closed-sc | 0.014 (n=141) | 0.019 (n=52) | 0.010 (n=399) |
| llama1b | closed | 0.007 (n=141) | 0.000 (n=52) | 0.010 (n=399) |
| llama1b | retrieve-given-gemma | 0.305 (n=141) | 0.173 (n=52) | 0.241 (n=399) |
| llama1b | retrieve-local | 0.454 (n=141) | 0.231 (n=52) | 0.311 (n=399) |
| llama1b | retrieve-oracle | 0.504 (n=141) | 0.269 (n=52) | 0.368 (n=399) |
| llama1b | retrieve-plus-local | 0.603 (n=141) | 0.173 (n=52) | 0.376 (n=399) |
| llama1b | retrieve | 0.213 (n=141) | 0.115 (n=52) | 0.135 (n=399) |
| llama3b | agentic-fewshot | 0.035 (n=141) | 0.019 (n=52) | 0.063 (n=399) |
| llama3b | agentic-local | 0.035 (n=141) | 0.000 (n=52) | 0.043 (n=399) |
| llama3b | agentic-scaffold | 0.106 (n=141) | 0.038 (n=52) | 0.055 (n=399) |
| llama3b | agentic | 0.035 (n=141) | 0.000 (n=52) | 0.043 (n=399) |
| llama3b | closed-sc | 0.035 (n=141) | 0.000 (n=52) | 0.045 (n=399) |
| llama3b | closed | 0.050 (n=141) | 0.000 (n=52) | 0.043 (n=399) |
| llama3b | retrieve-local | 0.801 (n=141) | 0.385 (n=52) | 0.576 (n=399) |
| llama3b | retrieve-oracle | 0.816 (n=141) | 0.423 (n=52) | 0.612 (n=399) |
| llama3b | retrieve-plus-local | 0.830 (n=141) | 0.365 (n=52) | 0.614 (n=399) |
| llama3b | retrieve | 0.305 (n=141) | 0.231 (n=52) | 0.281 (n=399) |
| mimir-hf | agentic-local | 0.106 (n=141) | 0.058 (n=52) | 0.133 (n=399) |
| mimir-hf | agentic-scaffold | 0.248 (n=141) | 0.058 (n=52) | 0.088 (n=399) |
| mimir-hf | agentic | 0.106 (n=141) | 0.038 (n=52) | 0.140 (n=399) |
| mimir-hf | closed | 0.113 (n=141) | 0.019 (n=52) | 0.083 (n=399) |
| mimir-hf | retrieve-given-gemma+qwen | 0.546 (n=141) | 0.385 (n=52) | 0.549 (n=399) |
| mimir-hf | retrieve-given-qwen | 0.454 (n=141) | 0.346 (n=52) | 0.496 (n=399) |
| mimir-hf | retrieve-local | 0.809 (n=141) | 0.442 (n=52) | 0.634 (n=399) |
| mimir-hf | retrieve-oracle | 0.823 (n=141) | 0.481 (n=52) | 0.677 (n=399) |
| mimir-hf | retrieve-plus-local | 0.837 (n=141) | 0.462 (n=52) | 0.707 (n=399) |
| mimir-hf | retrieve-plus-qwenq-local | - | - | 1.000 (n=1) |
| mimir-hf | retrieve | 0.369 (n=141) | 0.288 (n=52) | 0.316 (n=399) |
| mimir-official-prefix-t100 | closed | 0.113 (n=141) | 0.019 (n=52) | 0.083 (n=399) |
| mimir-official-t100 | closed | 0.099 (n=141) | 0.000 (n=52) | 0.045 (n=399) |
| mimir-official | closed | - | - | - |
| mimir | agentic-fewshot | 0.057 (n=141) | 0.000 (n=52) | 0.025 (n=399) |
| mimir | agentic-scaffold | 0.121 (n=141) | 0.115 (n=52) | 0.120 (n=399) |
| mimir | agentic | 0.092 (n=141) | 0.000 (n=52) | 0.040 (n=399) |
| mimir | closed-sc | 0.113 (n=141) | 0.000 (n=52) | 0.053 (n=399) |
| mimir | closed | 0.078 (n=141) | 0.000 (n=52) | 0.055 (n=399) |
| mimir | retrieve-given-gemma | 0.489 (n=141) | 0.308 (n=52) | 0.328 (n=399) |
| mimir | retrieve-given-qwen | 0.433 (n=141) | 0.231 (n=52) | 0.383 (n=399) |
| mimir | retrieve-oracle | 0.837 (n=141) | 0.365 (n=52) | 0.556 (n=399) |
| mimir | retrieve | 0.348 (n=141) | 0.192 (n=52) | 0.246 (n=399) |
| qwen3b | agentic-fewshot | 0.369 (n=141) | 0.327 (n=52) | 0.406 (n=399) |
| qwen3b | agentic-local | 0.723 (n=141) | 0.442 (n=52) | 0.509 (n=399) |
| qwen3b | agentic-scaffold | 0.326 (n=141) | 0.212 (n=52) | 0.266 (n=399) |
| qwen3b | agentic | 0.369 (n=141) | 0.269 (n=52) | 0.429 (n=399) |
| qwen3b | closed-sc | 0.043 (n=141) | 0.019 (n=52) | 0.030 (n=399) |
| qwen3b | closed | 0.043 (n=141) | 0.019 (n=52) | 0.028 (n=399) |
| qwen3b | retrieve-local | 0.759 (n=141) | 0.500 (n=52) | 0.554 (n=399) |
| qwen3b | retrieve-oracle | 0.801 (n=141) | 0.462 (n=52) | 0.589 (n=399) |
| qwen3b | retrieve-plus-local | 0.801 (n=141) | 0.538 (n=52) | 0.594 (n=399) |
| qwen3b | retrieve | 0.326 (n=141) | 0.269 (n=52) | 0.263 (n=399) |

## Retrieval-necessity confusion matrix: did the model know when to look? (call decision vs closed-book EM)

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
| mimir-hf | agentic | 54 | 488 | 2 | 48 | 0.96 | 0.10 |
| mimir-hf | agentic-scaffold | 87 | 455 | 7 | 43 | 0.93 | 0.16 |
| qwen3b | agentic | 574 | 0 | 18 | 0 | 0.97 | 1.00 |
| qwen3b | agentic-fewshot | 571 | 3 | 17 | 1 | 0.97 | 0.99 |
| qwen3b | agentic-scaffold | 566 | 8 | 18 | 0 | 0.97 | 0.99 |

## Reader accuracy given retrieval success (reading fidelity) vs distraction: EM when the gold answer was inside the retrieved intros vs not (retrieve condition)

| model | EM given answer present | n | EM given answer absent | n |
|---|---|---|---|---|
| gemma4b | 0.728 | 239 | 0.028 | 353 |
| llama1b | 0.368 | 239 | 0.006 | 353 |
| llama3b | 0.665 | 239 | 0.023 | 353 |
| mimir-hf | 0.745 | 239 | 0.042 | 353 |
| mimir | 0.590 | 239 | 0.045 | 353 |
| qwen3b | 0.644 | 239 | 0.031 | 353 |

## Can the model ask? Page-level precision of model-written queries (first Wikipedia hit is the subject page)

| model | variant | calls | first hit = subject | rate | empty results (fell back) |
|---|---|---|---|---|---|
| gemma4b | agentic-fewshot | 445 | 253 | 0.57 | 51 |
| gemma4b | agentic | 553 | 266 | 0.48 | 77 |
| llama1b | agentic-fewshot | 1 | 0 | 0.00 | 0 |
| llama1b | agentic | 0 | 0 | nan | 0 |
| llama3b | agentic-fewshot | 13 | 7 | 0.54 | 0 |
| llama3b | agentic | 0 | 0 | nan | 0 |
| mimir-hf | agentic | 56 | 51 | 0.91 | 1 |
| mimir | agentic-fewshot | 0 | 0 | nan | 0 |
| mimir | agentic | 0 | 0 | nan | 0 |
| qwen3b | agentic-fewshot | 588 | 295 | 0.50 | 135 |
| qwen3b | agentic | 592 | 308 | 0.52 | 155 |

## Default answers: most repeated predictions per run

| model | condition | top repeated predictions (count) | share of rows |
|---|---|---|---|
| gemma4b | agentic-fewshot | ukendt (15); ikke angivet (15); ikke nævnt (13) | 0.07 |
| gemma4b | agentic-local | ukendt (10); carl nielsen (9); kai normann andersen (8) | 0.05 |
| gemma4b | agentic-scaffold | ukendt (27); ikke nævnt (16); carl nielsen (11) | 0.09 |
| gemma4b | agentic | ikke angivet (23); ikke nævnt (18); carl nielsen (10) | 0.09 |
| gemma4b | closed-sc | carl nielsen (18); kim larsen (13); søren kierkegaard (10) | 0.07 |
| gemma4b | closed | carl nielsen (18); kim larsen (14); søren kierkegaard (9) | 0.07 |
| gemma4b | retrieve-local | kai normann andersen (12); ukendt (10); ikke angivet (7) | 0.05 |
| gemma4b | retrieve-oracle | ikke angivet (13); kai normann andersen (12); ukendt (10) | 0.06 |
| gemma4b | retrieve-plus-local | kai normann andersen (12); ukendt (6); ikke nævnt (5) | 0.04 |
| gemma4b | retrieve | ukendt (31); ikke nævnt (21); carl nielsen (10) | 0.10 |
| llama1b | agentic-fewshot | 2014 (22); 2010 (17); 2015 (11) | 0.08 |
| llama1b | agentic-local | mogens lindberg (12); 2014 (10); 1995 (10) | 0.05 |
| llama1b | agentic-scaffold | carl nielsen (11); niels w gade (8); 1998 (3) | 0.04 |
| llama1b | agentic | 2014 (14); 2010 (12); mogens lindberg (10) | 0.06 |
| llama1b | closed-sc | leonardo da vinci (16); ludwig van beethoven (4); mozart (4) | 0.04 |
| llama1b | closed | leonardo da vinci (14); mogens lindberg (9); 1995 (9) | 0.05 |
| llama1b | retrieve-given-gemma | kai normann andersen (5); niels w gade (4); 1998 (3) | 0.02 |
| llama1b | retrieve-local | kai normann andersen (5); 1956 (4); 1987 (3) | 0.02 |
| llama1b | retrieve-oracle | kai normann andersen (6); 1838 (5); børge og arvid m ller (5) | 0.03 |
| llama1b | retrieve-plus-local | kai normann andersen (6); 1838 (5); liva weel (4) | 0.03 |
| llama1b | retrieve | carl nielsen (11); niels w gade (8); 1998 (3) | 0.04 |
| llama3b | agentic-fewshot | jørgen leth (11); jørgen madsen (11); jeg er usikker på svaret (11) | 0.06 |
| llama3b | agentic-local | hans christian andersen (11); niels gade (9); jørgen madsen (9) | 0.05 |
| llama3b | agentic-scaffold | hans christian andersen (22); københavn (9); niels gade (8) | 0.07 |
| llama3b | agentic | hans christian andersen (13); jørgen madsen (10); niels gade (9) | 0.05 |
| llama3b | closed-sc | hans christian andersen (13); københavn (9); søren kierkegaard (8) | 0.05 |
| llama3b | closed | hans christian andersen (24); københavn (9); 1984 (8) | 0.07 |
| llama3b | retrieve-local | kai normann andersen (12); n f s grundtvig (4); 1838 (4) | 0.03 |
| llama3b | retrieve-oracle | kai normann andersen (12); 1838 (4); h c lumbye (4) | 0.03 |
| llama3b | retrieve-plus-local | kai normann andersen (10); 1987 (4); 1838 (4) | 0.03 |
| llama3b | retrieve | jeg er ikke klar over spørgs (9); jeg er ukendt (8); carl nielsen (7) | 0.04 |
| mimir-hf | agentic-local | præcis (47); søren kierkegaard (46); 2005 (18) | 0.19 |
| mimir-hf | agentic-scaffold | carl nielsen (24); hans christian andersen (14); johannes v jensen (13) | 0.09 |
| mimir-hf | agentic | præcis (47); søren kierkegaard (46); 2005 (18) | 0.19 |
| mimir-hf | closed | carl nielsen (25); hans christian andersen (14); johannes v jensen (13) | 0.09 |
| mimir-hf | retrieve-given-gemma+qwen | kai normann andersen (8); ukendt (5); 1978 (4) | 0.03 |
| mimir-hf | retrieve-given-qwen | kai normann andersen (7); ikke nævnt (6); niels w gade (5) | 0.03 |
| mimir-hf | retrieve-local | kai normann andersen (12); 1838 (4); h c lumbye (4) | 0.03 |
| mimir-hf | retrieve-oracle | kai normann andersen (12); 1838 (4); h c lumbye (4) | 0.03 |
| mimir-hf | retrieve-plus-local | kai normann andersen (12); 1987 (4); 1838 (4) | 0.03 |
| mimir-hf | retrieve-plus-qwenq-local | n f s grundtvig (1) | 1.00 |
| mimir-hf | retrieve | niels w gade (10); carl nielsen (9); ikke nævnt (8) | 0.05 |
| mimir-official-prefix-t100 | closed | carl nielsen (26); hans christian andersen (15); johannes v jensen (13) | 0.09 |
| mimir-official-t100 | closed | carl nielsen (26); mona lisa (16); 1973 (13) | 0.09 |
| mimir-official | closed |  | 0.00 |
| mimir | agentic-fewshot | 2000 (31); søren ulrik thomsen (19); svar carl nielsen (17) | 0.11 |
| mimir | agentic-scaffold | mona lisa (16); hans christian andersen (14); carl nielsen (14) | 0.07 |
| mimir | agentic | carl nielsen (18); mona lisa (17); 2000 (17) | 0.09 |
| mimir | closed-sc | carl nielsen (19); mona lisa (18); h c andersen (17) | 0.09 |
| mimir | closed | carl nielsen (27); hans christian andersen (20); mona lisa (19) | 0.11 |
| mimir | retrieve-given-gemma | carl nielsen (13); 1973 (8); kai normann andersen (5) | 0.04 |
| mimir | retrieve-given-qwen | kai normann andersen (6); 2000 (6); 1973 (5) | 0.03 |
| mimir | retrieve-oracle | kai normann andersen (11); poul reichhardt (4); 1978 (4) | 0.03 |
| mimir | retrieve | carl nielsen (11); niels w gade (7); 1973 (6) | 0.04 |
| qwen3b | agentic-fewshot | kai normann andersen (8); 1988 (4); carl nielsen (4) | 0.03 |
| qwen3b | agentic-local | kai normann andersen (10); liva weel (4); 1838 (4) | 0.03 |
| qwen3b | agentic-scaffold | carl nielsen (9); c e f weyse (8); poul reichhardt (4) | 0.04 |
| qwen3b | agentic | kai normann andersen (7); carl nielsen (5); børge m ller (4) | 0.03 |
| qwen3b | closed-sc | carl nielsen (18); hans christian andersen (10); 12 (9) | 0.06 |
| qwen3b | closed | carl nielsen (21); 12 (14); 1991 (9) | 0.07 |
| qwen3b | retrieve-local | kai normann andersen (12); n f s grundtvig (4); liva weel (4) | 0.03 |
| qwen3b | retrieve-oracle | kai normann andersen (12); liva weel (4); 1838 (4) | 0.03 |
| qwen3b | retrieve-plus-local | kai normann andersen (12); 1987 (4); 1838 (4) | 0.03 |
| qwen3b | retrieve | c e f weyse (8); carl nielsen (7); poul reichhardt (4) | 0.03 |

## What goes wrong, counted (rule-based taxonomy; first matching category wins)

| run | n | exact | format (contains gold) | refused / not found | empty | year within 5 | year off by more | no year given | copied a fetched title | default answer | other wrong entity |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gemma4b_agentic | 592 | 236 | 16 | 46 | 0 | 8 | 36 | 21 | 55 | 21 | 153 |
| gemma4b_closed | 592 | 33 | 4 | 0 | 0 | 21 | 116 | 0 | 0 | 39 | 379 |
| gemma4b_retrieve | 592 | 184 | 7 | 68 | 0 | 8 | 57 | 10 | 59 | 6 | 193 |
| llama1b_agentic | 592 | 5 | 8 | 1 | 0 | 8 | 123 | 8 | 0 | 11 | 428 |
| llama1b_closed | 592 | 5 | 12 | 2 | 0 | 9 | 127 | 3 | 0 | 24 | 410 |
| llama1b_retrieve | 592 | 90 | 62 | 1 | 0 | 14 | 71 | 12 | 79 | 5 | 258 |
| llama3b_agentic | 592 | 22 | 7 | 3 | 0 | 14 | 112 | 8 | 0 | 32 | 394 |
| llama3b_closed | 592 | 24 | 2 | 6 | 0 | 15 | 117 | 0 | 0 | 30 | 398 |
| llama3b_retrieve | 592 | 167 | 27 | 92 | 0 | 5 | 38 | 7 | 41 | 10 | 205 |
| mimir-hf_agentic | 592 | 73 | 9 | 2 | 0 | 8 | 118 | 0 | 5 | 91 | 286 |
| mimir-hf_closed | 592 | 50 | 7 | 1 | 0 | 12 | 113 | 0 | 0 | 52 | 357 |
| mimir-hf_retrieve | 592 | 193 | 15 | 14 | 0 | 15 | 72 | 1 | 79 | 6 | 197 |
| mimir-official-prefix-t100_closed | 592 | 50 | 7 | 1 | 0 | 11 | 114 | 0 | 0 | 54 | 355 |
| mimir-official-t100_closed | 592 | 32 | 15 | 0 | 0 | 12 | 114 | 0 | 0 | 42 | 377 |
| mimir-official_closed | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| mimir_agentic | 592 | 29 | 16 | 0 | 0 | 8 | 120 | 0 | 0 | 35 | 384 |
| mimir_closed | 592 | 33 | 13 | 0 | 0 | 14 | 116 | 0 | 0 | 66 | 350 |
| mimir_retrieve | 592 | 157 | 21 | 0 | 0 | 11 | 81 | 0 | 49 | 7 | 266 |
| qwen3b_agentic | 592 | 237 | 27 | 2 | 0 | 14 | 68 | 3 | 39 | 4 | 198 |
| qwen3b_closed | 592 | 18 | 6 | 0 | 0 | 14 | 120 | 1 | 0 | 32 | 401 |
| qwen3b_retrieve | 592 | 165 | 22 | 2 | 0 | 14 | 78 | 1 | 76 | 4 | 230 |


## Cost axis: tokens, lookups and seconds per question; exact match per 1k tokens and per second

| model | condition | n | EM | prompt tok/q | completion tok/q | lookups/q | s/q | EM per 1k tok | EM per s |
|---|---|---|---|---|---|---|---|---|---|
| mimir-hf | retrieve-plus-qwenq-local | 1 | 1.000 | 1248 | 10.0 | 1.00 | 79.1 | 0.79 | 0.013 |
| mimir-hf | retrieve-plus-local | 592 | 0.716 | 1302 | 6.0 | 1.00 | 43.5 | 0.55 | 0.016 |
| mimir-hf | retrieve-oracle | 592 | 0.694 | 708 | 5.8 | 1.00 | 8.6 | 0.97 | 0.081 |
| gemma4b | retrieve-plus-local | 592 | 0.688 | 1302 | 6.3 | 1.00 | 8.4 | 0.53 | 0.082 |
| gemma4b | retrieve-oracle | 592 | 0.679 | 708 | 6.2 | 1.00 | 3.6 | 0.95 | 0.188 |
| mimir-hf | retrieve-local | 592 | 0.659 | 944 | 6.1 | 1.00 | 26.2 | 0.69 | 0.025 |
| gemma4b | retrieve-local | 592 | 0.657 | 944 | 6.2 | 1.00 | 5.6 | 0.69 | 0.118 |
| llama3b | retrieve-oracle | 592 | 0.644 | 780 | 8.5 | 1.00 | 2.2 | 0.82 | 0.293 |
| llama3b | retrieve-plus-local | 592 | 0.644 | 1411 | 8.6 | 1.00 | 6.8 | 0.45 | 0.094 |
| qwen3b | retrieve-plus-local | 592 | 0.639 | 1449 | 6.5 | 1.00 | 6.4 | 0.44 | 0.099 |
| qwen3b | retrieve-oracle | 592 | 0.628 | 798 | 6.8 | 1.00 | 2.2 | 0.78 | 0.291 |
| llama3b | retrieve-local | 592 | 0.613 | 1029 | 9.3 | 1.00 | 4.4 | 0.59 | 0.141 |
| mimir | retrieve-oracle | 592 | 0.606 | 715 | 7.0 | 1.00 | 8.5 | 0.84 | 0.071 |
| qwen3b | retrieve-local | 592 | 0.598 | 1055 | 6.5 | 1.00 | 4.2 | 0.56 | 0.144 |
| qwen3b | agentic-local | 592 | 0.554 | 267 | 13.3 | 1.00 | 4.5 | 1.97 | 0.124 |
| mimir-hf | retrieve-given-gemma+qwen | 592 | 0.534 | 869 | 6.0 | 0.92 | 12.3 | 0.61 | 0.043 |
| llama3b | agentic-native-local | 143 | 0.490 | 1192 | 6.8 | 1.00 | 6.5 | 0.41 | 0.076 |
| gemma4b | agentic-local | 592 | 0.485 | 222 | 13.5 | 0.93 | 6.6 | 2.06 | 0.074 |
| mimir-hf | retrieve-given-qwen | 592 | 0.473 | 675 | 5.9 | 0.74 | 8.3 | 0.69 | 0.057 |
| llama1b | retrieve-plus-local | 592 | 0.412 | 1411 | 10.2 | 1.00 | 3.4 | 0.29 | 0.121 |
| qwen3b | agentic | 592 | 0.400 | 267 | 13.4 | 1.00 | 3.7 | 1.43 | 0.109 |
| gemma4b | agentic | 592 | 0.399 | 222 | 13.6 | 0.93 | 5.9 | 1.69 | 0.068 |
| gemma4b | agentic-fewshot | 592 | 0.397 | 314 | 13.4 | 0.75 | 5.2 | 1.21 | 0.076 |
| llama1b | retrieve-oracle | 592 | 0.392 | 780 | 11.0 | 1.00 | 0.9 | 0.50 | 0.420 |
| qwen3b | agentic-fewshot | 592 | 0.390 | 368 | 12.7 | 0.99 | 3.6 | 1.02 | 0.109 |
| mimir | retrieve-given-qwen | 592 | 0.382 | 682 | 7.6 | 0.74 | 9.3 | 0.55 | 0.041 |
| mimir | retrieve-given-gemma | 592 | 0.365 | 684 | 7.4 | 0.80 | 9.1 | 0.53 | 0.040 |
| llama1b | retrieve-local | 592 | 0.338 | 1029 | 11.6 | 1.00 | 2.0 | 0.32 | 0.166 |
| mimir-hf | retrieve | 592 | 0.326 | 658 | 5.8 | 1.00 | 8.1 | 0.49 | 0.040 |
| gemma4b | retrieve | 592 | 0.311 | 658 | 6.5 | 1.00 | 3.7 | 0.47 | 0.085 |
| gemma4b | agentic-scaffold | 592 | 0.289 | 607 | 6.4 | 0.88 | 4.7 | 0.47 | 0.061 |
| llama3b | retrieve | 592 | 0.282 | 727 | 11.8 | 1.00 | 2.9 | 0.38 | 0.097 |
| qwen3b | retrieve | 592 | 0.279 | 746 | 6.9 | 1.00 | 2.6 | 0.37 | 0.107 |
| qwen3b | agentic-scaffold | 592 | 0.275 | 738 | 6.7 | 0.99 | 2.9 | 0.37 | 0.094 |
| mimir | retrieve | 592 | 0.265 | 665 | 7.8 | 1.00 | 9.3 | 0.39 | 0.029 |
| llama1b | retrieve-given-gemma | 592 | 0.250 | 747 | 11.8 | 0.80 | 1.1 | 0.33 | 0.232 |
| qwen3b | agentic-native-local | 592 | 0.169 | 304 | 1.4 | 0.24 | 1.9 | 0.55 | 0.088 |
| llama1b | retrieve | 592 | 0.152 | 727 | 12.0 | 1.00 | 1.3 | 0.21 | 0.117 |
| llama1b | agentic-scaffold | 592 | 0.150 | 727 | 12.0 | 1.00 | 1.2 | 0.20 | 0.123 |
| mimir-hf | agentic-scaffold | 592 | 0.123 | 247 | 5.9 | 0.16 | 4.2 | 0.49 | 0.029 |
| mimir-hf | agentic | 592 | 0.123 | 222 | 7.1 | 0.09 | 3.3 | 0.54 | 0.037 |
| mimir-hf | agentic-local | 592 | 0.120 | 222 | 7.1 | 0.09 | 9.6 | 0.52 | 0.012 |
| mimir | agentic-scaffold | 592 | 0.120 | 319 | 7.5 | 0.31 | 8.3 | 0.37 | 0.014 |
| mimir-hf | closed | 592 | 0.084 | 166 | 5.9 | 0.00 | 1.9 | 0.49 | 0.045 |
| mimir-official-prefix-t100 | closed | 592 | 0.084 | 0 | 0.0 | 0.00 | 576.7 | nan | 0.000 |
| llama3b | agentic-scaffold | 592 | 0.066 | 263 | 6.9 | 0.12 | 1.0 | 0.24 | 0.064 |
| mimir | closed-sc | 592 | 0.062 | 173 | 7.8 | 0.00 | 20.2 | 0.35 | 0.003 |
| gemma4b | agentic-native-local | 592 | 0.056 | 0 | 0.0 | 0.00 | 1.2 | nan | 0.046 |
| gemma4b | closed | 592 | 0.056 | 166 | 5.3 | 0.00 | 1.2 | 0.33 | 0.046 |
| mimir | closed | 592 | 0.056 | 173 | 6.9 | 0.00 | 6.0 | 0.31 | 0.009 |
| gemma4b | closed-sc | 592 | 0.054 | 166 | 5.3 | 0.00 | 3.3 | 0.32 | 0.017 |
| mimir-official-t100 | closed | 592 | 0.054 | 0 | 0.0 | 0.00 | 593.5 | nan | 0.000 |
| llama3b | agentic-fewshot | 592 | 0.052 | 372 | 7.8 | 0.02 | 0.6 | 0.14 | 0.093 |
| mimir | agentic | 592 | 0.049 | 229 | 8.9 | 0.00 | 7.1 | 0.21 | 0.007 |
| llama3b | closed | 592 | 0.041 | 206 | 6.0 | 0.00 | 0.4 | 0.19 | 0.103 |
| llama3b | closed-sc | 592 | 0.039 | 206 | 6.1 | 0.00 | 1.5 | 0.18 | 0.026 |
| llama3b | agentic-local | 592 | 0.037 | 271 | 8.3 | 0.00 | 0.5 | 0.13 | 0.075 |
| llama3b | agentic | 592 | 0.037 | 271 | 8.5 | 0.00 | 0.5 | 0.13 | 0.074 |
| mimir | agentic-native-local | 592 | 0.032 | 0 | 0.0 | 0.00 | 8.7 | nan | 0.004 |
| qwen3b | closed-sc | 592 | 0.032 | 202 | 6.3 | 0.00 | 1.5 | 0.15 | 0.021 |
| mimir | agentic-fewshot | 592 | 0.030 | 321 | 9.1 | 0.00 | 7.4 | 0.09 | 0.004 |
| qwen3b | closed | 592 | 0.030 | 202 | 6.2 | 0.00 | 0.4 | 0.15 | 0.076 |
| llama1b | agentic-fewshot | 592 | 0.014 | 372 | 10.2 | 0.00 | 0.2 | 0.04 | 0.057 |
| llama1b | closed-sc | 592 | 0.012 | 206 | 10.9 | 0.00 | 1.0 | 0.05 | 0.012 |
| llama1b | agentic | 592 | 0.008 | 271 | 10.5 | 0.00 | 0.2 | 0.03 | 0.036 |
| llama1b | closed | 592 | 0.008 | 206 | 12.6 | 0.00 | 0.3 | 0.04 | 0.033 |
| llama1b | agentic-local | 592 | 0.007 | 271 | 10.5 | 0.00 | 0.2 | 0.02 | 0.029 |

