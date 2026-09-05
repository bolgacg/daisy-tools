"""Apply the prefix-LM prompt-attention change to a llama.cpp tree that has the hrm-text model (PR 27625)."""
import sys
root = sys.argv[1] if len(sys.argv) > 1 else "."
def sub(path, old, new):
    s = open(path, encoding="utf-8").read()
    assert old in s, (path, old[:50]); assert new not in s, ("already applied", path)
    open(path, "w", encoding="utf-8").write(s.replace(old, new, 1))
p = f"{root}/src/llama-context.cpp"
sub(p, '''    GGML_ASSERT((cparams.causal_attn || cparams.n_ubatch >= n_tokens_all) && "non-causal attention requires n_ubatch >= n_tokens");
''', '''    GGML_ASSERT((cparams.causal_attn || cparams.n_ubatch >= n_tokens_all) && "non-causal attention requires n_ubatch >= n_tokens");

    if (model.hparams.hrm_prefix_lm && n_tokens_all > 1 && n_tokens_all > cparams.n_ubatch) {
        LLAMA_LOG_WARN("%s: prefix-LM prompt of %d tokens exceeds n_ubatch = %d; prompt tokens in different chunks will not see each other (use n_ubatch >= prompt length)\\n",
                __func__, n_tokens_all, cparams.n_ubatch);
    }
''')
sub(p, '''        ggml_status status;

        const auto * res = process_ubatch(ubatch, ctx_type_to_graph_type(cparams.ctx_type), mctx.get(), status);

        if (!res) {
            // the last ubatch failed or was aborted -> remove all positions of that ubatch from the memory module''',
'''        ggml_status status;

        // prefix-LM models (hrm-text): the prompt is attended in both directions, generated tokens causally.
        // a multi-token ubatch is prompt processing, a single-token ubatch is generation
        const bool causal_attn_org = cparams.causal_attn;
        if (model.hparams.hrm_prefix_lm) {
            cparams.causal_attn = ubatch.n_tokens == 1;
        }

        const auto * res = process_ubatch(ubatch, ctx_type_to_graph_type(cparams.ctx_type), mctx.get(), status);

        cparams.causal_attn = causal_attn_org;

        if (!res) {
            // the last ubatch failed or was aborted -> remove all positions of that ubatch from the memory module''')
sub(f"{root}/src/models/hrm-text.cpp", "    // prefix-LM prefill is not implemented (causal attention only); kept for round-trip\n",
    "    // prefix-LM: the prompt is attended bidirectionally in llama_context::decode when this is set\n")
print("applied to", root)
