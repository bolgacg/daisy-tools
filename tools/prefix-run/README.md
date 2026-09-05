# prefix-run: Mimir's prompt attention in llama.cpp

DFM-Mimir is a prefix language model: while it reads the prompt, every prompt token attends to
every other prompt token in both directions; only the answer is generated left to right. The
community llama.cpp port (ggml-org/llama.cpp pull request 27625) reads the prompt left to right
only. On DAISY that costs a third of the score (5.6 against 8.4 exact match, same GGUF, same
questions, see results/).

This folder holds two ways to get the right attention, and a checker.

## 1. The patch (the one to use)

`patch/apply_prefixlm.py` edits a llama.cpp tree that already has the hrm-text model (the PR
branch). `patch/0001-*.patch` is the same change as a git patch. Thirty-five lines in six files:

- `src/llama-kv-cache.cpp`: for models with `prefix_lm` set the KQ mask is not causal. A token
  attends to every token of its own sequence in the cache or in the current ubatch. Generation
  appends one token per sequence per step, so generated tokens still see only earlier tokens.
  That is bidirectional over the prompt and causal over the answer, the training-time mask.
- `src/llama-context.cpp`: warns when a batch is split into ubatches, because prompt tokens in
  different ubatches cannot see each other. Run with `-ub` at least the longest prompt.
- `include/llama.h`, `src/llama-model.cpp`: `llama_model_is_prefix_lm()`.
- `tools/server/server-context.cpp`: prompt caching off for these models. A cached prompt prefix
  was computed without the tokens that follow it, so reusing it is wrong for a prefix LM.

Build and serve:

    python patch/apply_prefixlm.py /path/to/llama.cpp
    cmake --build /path/to/llama.cpp/build -j --target llama-server
    llama-server -m DFM-Mimir-Q8_0.gguf -c 8192 -b 4096 -ub 4096 -np 2 --jinja -fa on --reasoning off

`--reasoning off` matters for benchmark numbers: llama.cpp defaults `enable_thinking` to true and
then renders Mimir's template with a system turn containing `<|think|>`; the Hugging Face template
renders no system turn by default, and the group's numbers come from that prompt.

## 2. The driver (no llama.cpp change)

`prefix-run.cpp` uses the public `llama_set_causal_attn()` API: attention off for the prompt
batch, on for generation. `make_prompts.py` writes the prompts as token ids with the Hugging Face
chat template, `build.sh` compiles the driver against a built llama.cpp tree. It is slower than the
server (the scheduler re-reserves when the mode flips) and it is what produced the first 94 percent
word-identical check against the official transformers output. With the patch applied, the
driver's `--causal` flag has no effect: the mask ignores the causal setting for prefix-LM models.

## 3. The checker

`compare_server.py` asks a running server the same questions as a reference run and prints the
share of word-identical answers after the DAISY normaliser, plus exact match for both:

    python tools/prefix-run/compare_server.py --ref results/pred_mimir-official-prefix-t100_closed.jsonl \
        --model mimir-prefix --n 592 --config default

`--config` can also switch prompt caching and thinking off per request, which is how the two
causes of the earlier 42 percent word identity were found (caching on: 14 of 40 identical; off: 23
of 40; the thinking system turn explains most of the rest).
