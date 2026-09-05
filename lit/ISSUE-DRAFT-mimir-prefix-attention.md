# Draft, NOT filed. Needs Bo's approval of the exact text and of where it goes (llama.cpp PR #27625 thread, the noctrex GGUF
# model card, or the DFM-Mimir model card discussion on Hugging Face). Numbers from results/ (5 Sep 2026).

Title: DFM-Mimir loses about a third of its DAISY score under causal-only prompt attention

DFM-Mimir is trained as a prefix LM (config: prefix_lm true): the prompt is attended bidirectionally and only the
completion is causal. The current GGUF conversion and the llama.cpp implementation in PR #27625 run the prompt with causal
attention only. On the public DAISY benchmark (schneiderkamplab/SDU-Daisy, 592 questions, the group's own prompt, greedy,
100 new tokens, the group's exact-match scorer) this is what the same weights score:

| Path | Exact match |
|---|---|
| transformers, official implementation, prefix attention (token_type_ids = 1 over the prompt) | 8.4 % |
| transformers, official implementation, causal attention over the prompt | 5.4 % |
| llama.cpp (PR #27625), Q8_0 GGUF, causal only, 64 new tokens | 5.6 % |
| Reported in the Mimir paper (Inspect harness) | 9.6 % |

Prefix versus causal on the identical code path is 8.4 against 5.4, so the attention mode, not quantisation, explains the
gap between the port and the paper. With one Wikipedia lookup in front of the question the effect is smaller but still
present (official prefix 65.9 % versus the port's reading fidelity trailing by several points on identical fetched text).

Reproduction: github.com/bolgacg/daisy-tools, scripts/mimir_official.py --prefix / (no flag), and results/pred_mimir-official-*.jsonl.

Suggested fix: expose a prefix (non-causal prompt) attention mode for this architecture in llama.cpp, or state on the GGUF
card that scores under causal-only attention are not comparable to the paper's.
