"""Apply the prefix-LM attention change to a llama.cpp tree that has the hrm-text model (PR 27625).

Four edits:
  1. llama-kv-cache: for prefix-LM models the KQ mask is not causal (a token attends to every token
     of its own sequence in the cache or the current ubatch; generation appends one token per step,
     so generated tokens still see only the past).
  2. llama-context: warn when a prompt is longer than n_ubatch (tokens in different ubatches cannot
     see each other).
  3. llama.h / llama-model: llama_model_is_prefix_lm(), same shape as llama_model_is_diffusion().
  4. llama-server: prompt caching off for prefix-LM models (a cached prefix was computed without the
     tokens that follow it), as the default and for requests that ask for it.
Usage: python apply_prefixlm.py /path/to/llama.cpp
"""
import sys
root = sys.argv[1] if len(sys.argv) > 1 else "."

def sub(path, old, new):
    s = open(path, encoding="utf-8").read()
    assert old in s, (path, old[:60])
    assert new not in s, ("already applied", path)
    open(path, "w", encoding="utf-8").write(s.replace(old, new, 1))

# 1. the mask
sub(f"{root}/src/llama-kv-cache.cpp",
'''void llama_kv_cache::set_input_kq_mask(ggml_tensor * dst, const llama_ubatch * ubatch, bool causal_attn) const {
    const uint32_t n_tokens = ubatch->n_tokens;
''',
'''void llama_kv_cache::set_input_kq_mask(ggml_tensor * dst, const llama_ubatch * ubatch, bool causal_attn) const {
    const uint32_t n_tokens = ubatch->n_tokens;

    // prefix-LM models (hrm-text with prefix_lm set): a token attends to every token of its own
    // sequence that is in the cache or in the current ubatch. Generation appends one token per
    // sequence per step, so generated tokens still see only earlier tokens. The result is
    // bidirectional attention over the prompt and causal attention over the answer, which is the
    // mask these models are trained with. The prompt has to be processed in one ubatch for this
    // to hold; llama_context::decode warns when it is not.
    if (hparams.hrm_prefix_lm) {
        causal_attn = false;
    }
''')

# 2. the warning
sub(f"{root}/src/llama-context.cpp",
'''    GGML_ASSERT((cparams.causal_attn || cparams.n_ubatch >= n_tokens_all) && "non-causal attention requires n_ubatch >= n_tokens");
''',
'''    GGML_ASSERT((cparams.causal_attn || cparams.n_ubatch >= n_tokens_all) && "non-causal attention requires n_ubatch >= n_tokens");

    if (model.hparams.hrm_prefix_lm && n_tokens_all > cparams.n_ubatch) {
        LLAMA_LOG_WARN("%s: prefix-LM: a batch of %d tokens is split into ubatches of %d; prompt tokens in different ubatches do not see each other (use -ub >= the longest prompt)\\n",
                __func__, n_tokens_all, cparams.n_ubatch);
    }
''')

# 3. the API
sub(f"{root}/include/llama.h",
'''    // Returns true if the model is diffusion-based (like LLaDA, Dream, etc.)
    LLAMA_API bool llama_model_is_diffusion(const struct llama_model * model);
''',
'''    // Returns true if the model is diffusion-based (like LLaDA, Dream, etc.)
    LLAMA_API bool llama_model_is_diffusion(const struct llama_model * model);

    // Returns true if the model is a prefix LM: prompt tokens attend to each other in both
    // directions and only generated tokens are causal (like hrm-text with prefix_lm set).
    // Prompts must be processed in a single ubatch and cached prompt prefixes must not be reused.
    LLAMA_API bool llama_model_is_prefix_lm(const struct llama_model * model);
''')
sub(f"{root}/src/llama-model.cpp",
'''bool llama_model_is_diffusion(const llama_model * model) {
    return llm_arch_is_diffusion(model->arch);
}
''',
'''bool llama_model_is_diffusion(const llama_model * model) {
    return llm_arch_is_diffusion(model->arch);
}

bool llama_model_is_prefix_lm(const llama_model * model) {
    return model->hparams.hrm_prefix_lm;
}
''')

# 4. the server
sub(f"{root}/tools/server/server-context.cpp",
'''        if (ctx_tgt == nullptr) {
            SRV_ERR("failed to create_context with model '%s'\\n", params_base.model.path.c_str());
''',
'''        if (llama_model_is_prefix_lm(model_tgt) && params_base.cache_prompt) {
            SRV_WRN("%s", "prefix-LM model: prompt caching disabled, a cached prompt prefix would have been computed without the tokens that follow it\\n");
            params_base.cache_prompt = false;
        }

        if (ctx_tgt == nullptr) {
            SRV_ERR("failed to create_context with model '%s'\\n", params_base.model.path.c_str());
''')
sub(f"{root}/tools/server/server-context.cpp",
'''    bool launch_slot_with_task(server_slot & slot, server_task && task) {
        // process per-request lora adapters
''',
'''    bool launch_slot_with_task(server_slot & slot, server_task && task) {
        // prefix-LM models: the whole prompt is recomputed for every request
        if (task.params.cache_prompt && llama_model_is_prefix_lm(model_tgt)) {
            task.params.cache_prompt = false;
        }

        // process per-request lora adapters
''')

# 5. the comment in the model file
sub(f"{root}/src/models/hrm-text.cpp",
    "    // prefix-LM prefill is not implemented (causal attention only); kept for round-trip\n",
    "    // prefix-LM: prompt tokens attend to each other in both directions (see llama_kv_cache::set_input_kq_mask)\n")
print("applied to", root)
