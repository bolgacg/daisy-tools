// prefix-run: run a prefix-LM model (DFM Mimir) through llama.cpp with the prompt read in both directions.
// The prompt batch is decoded with causal attention off, so every prompt token attends to every other prompt
// token; generation then runs with causal attention on. No change to llama.cpp is needed: it uses the public
// llama_set_causal_attn API. --causal runs the ordinary left-to-right path for comparison.
//
// input: JSONL with {"id": ..., "ids": [token ids of the templated prompt], "gold": ...}
// output: JSONL with {"id", "gold", "prediction", "mode", "n_prompt", "n_gen"}
#include <cmath>
#include "llama.h"
#include "nlohmann/json.hpp"
#include <cstdio>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>
#include <algorithm>
using json = nlohmann::json;

int main(int argc, char ** argv) {
    std::string model_path, in_path, out_path; int max_new = 100, ngl = 99, n_ctx = 4096, threads = 4; bool causal = false; int limit = 0; int swa_full = 1; int n_outputs_max = 0; int dump_top = 0;
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "-m") model_path = argv[++i]; else if (a == "-i") in_path = argv[++i]; else if (a == "-o") out_path = argv[++i];
        else if (a == "-n") max_new = atoi(argv[++i]); else if (a == "-ngl") ngl = atoi(argv[++i]); else if (a == "-c") n_ctx = atoi(argv[++i]);
        else if (a == "-t") threads = atoi(argv[++i]); else if (a == "--causal") causal = true; else if (a == "--limit") limit = atoi(argv[++i]); else if (a == "--swa-full") swa_full = atoi(argv[++i]); else if (a == "--n-outputs-max") n_outputs_max = atoi(argv[++i]); else if (a == "--dump-top") dump_top = atoi(argv[++i]);
    }
    if (model_path.empty() || in_path.empty() || out_path.empty()) { fprintf(stderr, "usage: prefix-run -m model.gguf -i prompts.jsonl -o out.jsonl [-n 100] [-ngl 99] [--causal] [--limit N]\n"); return 1; }
    llama_backend_init();
    llama_model_params mp = llama_model_default_params(); mp.n_gpu_layers = ngl;
    llama_model * model = llama_model_load_from_file(model_path.c_str(), mp);
    if (!model) { fprintf(stderr, "model load failed\n"); return 1; }
    const llama_vocab * vocab = llama_model_get_vocab(model);
    llama_context_params cp = llama_context_default_params();
    cp.n_ctx = n_ctx; cp.n_batch = n_ctx; cp.n_ubatch = n_ctx; cp.n_seq_max = 1; cp.n_threads = threads; cp.n_threads_batch = threads; cp.swa_full = swa_full != 0; if (n_outputs_max > 0) cp.n_outputs_max = n_outputs_max;
    llama_context * ctx = llama_init_from_model(model, cp);
    if (!ctx) { fprintf(stderr, "context failed\n"); return 1; }
    std::ifstream in(in_path); std::ofstream out(out_path, std::ios::app);
    // resume: skip ids already written
    std::vector<std::string> done; { std::ifstream prev(out_path); std::string l; while (std::getline(prev, l)) { if (l.empty()) continue; try { done.push_back(json::parse(l)["id"].get<std::string>()); } catch (...) {} } }
    std::string line; int n_done = 0, n_seen = 0;
    const int n_vocab = llama_vocab_n_tokens(vocab);
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        json row = json::parse(line);
        std::string id = row["id"].get<std::string>();
        if (std::find(done.begin(), done.end(), id) != done.end()) continue;
        if (limit && n_seen >= limit) break; n_seen++;
        std::vector<llama_token> toks; for (auto & t : row["ids"]) toks.push_back(t.get<llama_token>());
        llama_memory_clear(llama_get_memory(ctx), true);
        llama_set_causal_attn(ctx, causal);                 // prompt: both directions unless --causal
        llama_batch batch = llama_batch_get_one(toks.data(), (int32_t) toks.size());
        if (llama_decode(ctx, batch) != 0) { fprintf(stderr, "decode failed on %s\n", id.c_str()); continue; }
        llama_set_causal_attn(ctx, true);                   // generation: left to right
        std::string text; int n_gen = 0; llama_token cur; json top1 = json::array(); std::vector<int> gen_ids;
        for (; n_gen < max_new; ++n_gen) {
            const float * logits = llama_get_logits_ith(ctx, -1);
            cur = (llama_token) (std::max_element(logits, logits + n_vocab) - logits);
            if (dump_top > 0 && n_gen == 0) {                // top-K of the first generation step as log-probabilities
                double mx = logits[cur], lse = 0; for (int i = 0; i < n_vocab; ++i) lse += std::exp((double) logits[i] - mx); lse = mx + std::log(lse);
                std::vector<int> idx(n_vocab); for (int i = 0; i < n_vocab; ++i) idx[i] = i;
                std::partial_sort(idx.begin(), idx.begin() + dump_top, idx.end(), [&](int a, int b) { return logits[a] > logits[b]; });
                for (int k = 0; k < dump_top; ++k) { char b[64]; int n = llama_token_to_piece(vocab, idx[k], b, sizeof(b), 0, true); top1.push_back({idx[k], (double) logits[idx[k]] - lse, std::string(b, n > 0 ? n : 0)}); }
            }
            gen_ids.push_back(cur);
            if (llama_vocab_is_eog(vocab, cur)) break;
            char buf[256]; int n = llama_token_to_piece(vocab, cur, buf, sizeof(buf), 0, true);
            if (n > 0) text.append(buf, n);
            llama_batch b1 = llama_batch_get_one(&cur, 1);
            if (llama_decode(ctx, b1) != 0) { fprintf(stderr, "gen decode failed on %s\n", id.c_str()); break; }
        }
        json o = {{"id", id}, {"gold", row.value("gold", "")}, {"prediction", text}, {"mode", causal ? "causal" : "prefix"}, {"n_prompt", (int) toks.size()}, {"n_gen", n_gen}, {"gen_ids", gen_ids}}; if (dump_top > 0) o["top1"] = top1;
        out << o.dump() << "\n"; out.flush(); n_done++;
        if (n_done % 25 == 0) fprintf(stderr, "%d rows\n", n_done);
    }
    fprintf(stderr, "done %d rows -> %s\n", n_done, out_path.c_str());
    llama_free(ctx); llama_model_free(model); llama_backend_free();
    return 0;
}
