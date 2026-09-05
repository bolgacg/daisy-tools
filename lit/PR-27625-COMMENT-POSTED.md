Mimir scores a third lower than it should when llama.cpp runs it, and the cause is how
the prompt is read.

DFM-Mimir is a Danish 1B model. It was trained as a prefix language model. That means:
while it reads the prompt, every token can see every other token in the prompt, in both
directions. Only the answer is generated one token at a time, left to right. The model's
config file says this (prefix_lm: true).

This PR reads the prompt left to right only, the way an ordinary causal model does. So
the model reads its input in a way it was never trained for.

I measured the effect on DAISY, a public Danish quiz of 592 questions made by the same
group that made Mimir. Same weights, same questions, their prompt, their exact-match
scorer, greedy decoding. Only the way the prompt is read changes:

  official transformers code, prompt read in both directions   8.4 %
  official transformers code, prompt read left to right only   5.4 %
  this PR, Q8_0 GGUF, left to right only                       5.6 %
  the number the Mimir paper reports                           9.6 %

The first two rows use the same code and differ only in attention mode: 8.4 against 5.4.
So the attention mode explains the gap to the paper. Quantisation does not: the Q8_0
GGUF scores the same as the unquantised model in the same mode.

Script and logged outputs: github.com/bolgacg/daisy-tools
(scripts/mimir_official.py --prefix, results/pred_mimir-official-*).

What would fix it is an attention mode for this architecture where the prompt is read in
both directions and only the generated tokens are causal, which is how the model was
trained. Until then, a short note on the model card that scores from this port are lower
than the paper's would help anyone comparing numbers. I am happy to rerun the benchmark
on any change.
