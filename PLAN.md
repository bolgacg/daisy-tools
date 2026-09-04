# daisy-tools: does a lookup tool close the gap for a 1B Danish model? (started 2 Sep 2026)

Purpose: artifact for SDU job 4203 (PhD AI, Schneider-Kamp, deadline Mon 7 Sep 23:59 CEST).
Kill rule (Bo): if it does not finish cleanly by Sat 5 Sep it is not mentioned anywhere.

## Their assets (all public, checked 2 Sep 22:45)
- Model: danish-foundation-models/DFM-Mimir, 1B HRM (model_type hrm_text, 16 layers, d=1536,
  vocab 262k), instruction-tuned with chat template, safetensors bf16 3.57 GB, Apache 2.0,
  standard transformers (no trust_remote_code). Model card reports Daisy among Danish benchmarks.
  GGUF: noctrex/DFM-Mimir (Q8_0 1.91 GB, BF16/F16 3.59 GB) but needs llama.cpp PR #27625,
  NOT mainline (grep of llama-arch.cpp: no hrm). No Q4 exists.
- Benchmark: HF dataset schneiderkamplab/SDU-Daisy (MIT): 592 rows id/Question/Answer/Subject,
  Danish, short factual answers (names, years, sizes). GitHub schneiderkamplab/SDU-Daisy
  (vendored in vendor/): evaluation/eval.py = EM, token F1, BLEU (smoothing method4), the
  official Danish prompt template, OpenAI-compatible runner; model_evals/ = predictions of five
  big models (Llama-3.3-70B etc.). public/questions.csv = 740 ids (larger than the 592 with gold).
- Observation: even Llama-3.3-70B hallucinates on these (q2 gold 1824, pred 1957; q5 pred
  "Christopher Tolkien"). Retrieval should matter a lot; the question is whether a 1B model can
  USE it (read the snippet, extract, not get distracted) and whether it knows WHEN to call.

## Design (principled, small, honest)
Conditions, same 592 questions, temperature 0, official prompt:
  A. Mimir closed-book (reproduces their number; sanity check against the model card).
  B. Mimir + always-retrieve: Danish Wikipedia search (da.wikipedia.org API, opensearch + extract)
     for the question, top-k snippets in context.
  C. Mimir agentic: model may emit a tool call (search: <query>) or answer; one tool round.
  D. Oracle upper bound: retrieval with the gold-supported page (if cheap) or skip.
Report: EM/F1/BLEU per condition, per Subject; tool-call rate and precision in C; failure
taxonomy (tool not called, wrong query, snippet ignored, snippet contradicted). Release code.

## Compute paths
1. Box computer (Bo's friend's PC, inspected 3 Sep): ASUS Maximus V Gene (Z77, BIOS 1903),
   i5-3570K 4c/4t 3.4 GHz (Ivy Bridge, AVX but NO AVX2), 2x 8 GB DDR3-1600 (Kingston +
   Corsair Vengeance LP; the Corsair was unseated, BIOS showed 8 GB), **MSI GeForce GTX 1060
   6 GB OCV1** (Pascal sm_61, dp4a ok, fp16 slow-path but memory-bound decode is fine),
   Kingston SATA SSD(s) present but were unplugged (BIOS: 0 Drive), CMOS battery flat.
   Plan: Ubuntu Server 24.04 + SSH over Ethernet; llama.cpp CUDA build of PR #27625 with the
   Q8_0 GGUF (primary) or transformers fp16 on GPU with an sm_61-capable torch build (backup;
   CUDA 12.8+ torch wheels dropped Pascal, use a cu126 build). Expect the full 592 x 3 run in
   well under an hour on the GPU.
2. Colab free T4 with the official transformers snippet; results saved to Bo's Drive; Bo
   starts the notebook, I read results via the Drive connector.
3. Laptop (3.8 GB RAM, 4 cores): cannot hold Mimir (Q8 1.9 GB + KV + Python = OOM risk,
   WSL has crashed twice). Fallback only: small mainline model, weaker story.

## Box setup log (3 Sep)
- Bo: "full linux, no windows wanted" (Windows later on the second SSD if ever). Both SSDs are
  Kingston A400 480 GB (SA400S37480G) on Intel SATA ports 1 and 2 (moved off the ASMedia E ports,
  which the POST screen never lists). RAM now 16 GB after reseating the Corsair stick.
- Installer stick: Bo's 58.6 GB USB stick, Ventoy 1.1.17 written from WSL via PowerShell
  RunAs (C:\Users\bolga\ventoy), ubuntu-24.04.4-live-server-amd64.iso copied by
  ~/Downloads/iso/finish-stick.sh (status in stick-status.txt).
- Network: no Wi-Fi antenna seen, Ethernet impossible. Plan: install offline, then phone USB
  tethering; laptop joins the same phone hotspot for direct SSH, or Tailscale on the box.
  Permanent: USB Wi-Fi dongle with in-kernel driver (MediaTek MT7612U/MT7921AU), ~100-150 kr.

- 3 Sep 20:00: Ubuntu Server 24.04.4 installed on sda (LVM, root grown to 437 GB), user bo
  (installer saved it as "no", renamed in recovery), my ed25519 key in authorized_keys,
  passwordless sudo (/etc/sudoers.d/bo), tz Europe/Copenhagen, NTP synced. lspci: GTX 1060 6GB
  (GP106 rev a1), 15 GiB RAM, kernel 6.8.0-100. iPhone tether = enx* via netplan 'tether'
  (dhcp4, optional) at 172.20.10.8/28; laptop 172.20.10.3 on the same hotspot. Tailscale 1.102.3
  installed, `tailscale up --hostname gene` waiting for Bo's login. Driver plan:
  nvidia-driver-580-server (580.173.02, last branch with Pascal; 590+ dropped it), CUDA 12.x
  toolkit (CUDA 13 dropped Pascal). Heavy downloads WAIT for the Android tether: iPhone hotspot
  shares cellular, not Wi-Fi, so everything now rides Bo's mobile data.

## Their protocol, from the papers (read 3 Sep 21:20)
- DAISY paper (arXiv 2601.19930): 741 QA, zero-shot, "Prompt Template Version 1" (= eval.py PROMPT_TEMPLATE),
  answers normalised (case, punctuation, articles, whitespace), metrics = word-level F1 and NLTK
  sentence_bleu with SmoothingFunction().method4. Table: gpt-oss-20b 0.062/0.112, gpt-oss-120b
  0.126/0.211, gemma-3-27b-it 0.123/0.193, Llama-3.3-70B-Instruct 0.166/0.268 (best),
  Mistral-Small-3.1-24B 0.124/0.202 (BLEU/F1). Failure hypothesis: nationally bounded knowledge is a
  weak training signal; alignment biases toward cautious generic answers. The public HF set has 592
  golds (the repo's questions.csv has 740 ids; predictions cover 740). Our rescoring on the 592 is the
  replication anchor (results/replication_big_models_public592.json).
- Mimir paper (arXiv 2608.13517) Table 9 reports Daisy as EM: Mimir 1B 9.6, Gemma 4 E2B 5.6,
  Munin-Qwen 9B 5.4, Qwen 3.5 4B 4.7, Gemma 3 1B 1.4, Qwen 3.5 0.8B 0.7, HRM-Text 1B 0.0, OLMo 2 1B 0.0.
  All Danish tasks 0-shot, greedy (temperature 0), max_tokens 2048 for generation tasks; Gemma-4 chat
  template. "Agentic & tool use" data = 9.46% of the corpus; RL is stated future work.
  => Our closed-book Mimir EM on the 592 should land near 9.6; that is the sanity check.

## Research programme for the box (Bo, 3 Sep: "replicate their setup, add our modifications, run the
## same baselines, run llama as another baseline, compare")
1. Replicate: rescore their five big-model prediction files on the public 592 (done locally).
2. Closed-book small models at greedy/0-shot with their prompt: Mimir 1B (Q8), Llama-3.2-1B/3B-Instruct,
   Gemma-3-4b-it, Qwen2.5-3B-Instruct. Sanity: Mimir EM ~ 9.6.
3. Our modification: retrieve (shaped query, top-3 Danish Wikipedia intros) and agentic (model decides,
   one SEARCH round) for every model. Read gains against the retrieval ceiling (shaped ~41%, oracle
   subject ~81%, raw question ~22%).
4. Compare Danish-native 1B (Mimir) vs multilingual 1B/3B (Llama) with and without the tool: does
   Danish pretraining beat retrieval, or does retrieval erase the gap?
5. Improve: prompt variants for query formulation, k and snippet length sweeps, answer-type analysis
   (year/number/text), failure taxonomy with counts. Everything logged per row.

See IDEAS.md for the two idea loops (3 Sep).

## Status (3 Sep 22:05)
- [x] Repo vendored, dataset (592 golds) in data/daisy.jsonl, their metrics ported verbatim.
- [x] Harness: wiki tool (cache, pacing, 429 back-off), query shaper, 6-condition runner with
      parallel requests, scorer, report generator, smoke script; all synced to the box (~/daisy-tools).
- [x] Box ready: driver 580.173.02, CUDA 12.8, llama.cpp PR #27625 built with CUDA (arch 61);
      Mimir answers (gen 4.2 tok/s, prompt 143 tok/s: slow HRM loop); Llama 1B 86 tok/s, 3B 35 tok/s.
      Five GGUFs downloaded. Server flags: -c 12288 -np 3 -ctk/-ctv q8_0 --jinja -fa on.
- [x] Replication rescoring + retrieval ceilings done (see RESULTS sections).
- [x] Full run launched 22:00 (order llama1b, mimir, llama3b, gemma4b, qwen3b; 6 conditions each);
      logs/run_all.log; results/RESULTS.md at the end. Smoke test: Llama 1B never emits SEARCH.
- Early read 22:45: Mimir closed EM 0.056 strict / 0.078 lenient (paper 9.6 on 741; answers short,
  no truncation, 13 near-misses like "Forlaget Gyldendal"; default-answer collapse: "Carl Nielsen" x27,
  "Hans Christian Andersen" x23, "Mona Lisa" x19). Retrieval: Mimir 0.056 -> 0.265, Llama1B 0.008 ->
  0.152 (oracle query 0.392). Reading fidelity given answer present: Mimir 0.59 vs Llama1B 0.37.
  Agentic: neither 1B model ever emits SEARCH (0/592 Llama, 0/65 Mimir so far) => scaffold condition
  added (run_extra.sh). Ceilings final: question 0.215, shaped 0.404, subject 0.787.
- 03:10 read: Gemma-3-4B and Qwen2.5-3B DO call the tool (553/592 and 592/592) and their agentic EM
  (0.40 both) BEATS retrieval with my shaped query (0.31/0.28): model-written queries land better than
  the heuristic. Closed-book they are as weak as Mimir (0.056/0.030). Oracle-query ceiling 0.68/0.63.
  Llama 3B: closed 0.041, retrieve 0.282, oracle 0.644, calls 13/592 only with few-shot. Mimir never
  calls. Self-consistency: no effect anywhere. Decision quality: at 3-6% closed-book accuracy,
  "always search" is near-optimal, so call precision is inflated; the real decision problem needs a
  model that knows a lot (70B). Say so on the page.
- 05:05: main run complete (5 models x 6 conditions); scaffold run in progress (mimir slow). Results page
  built at site/ (index.html, page.css, app.js, data.js from scripts/build_page_data.py), house style,
  spotlight tour, headless walk clean at 1536 and 390 (0 errors, 0 overflow). Local git repo initialised
  (author Bo). NOT published: remote repo + Pages wait for Bo's review and OK. Letter artifact block and CV
  entry filled with the numbers. Remaining: final scaffold numbers, PDFs, Bo review, publish, misc bundle.
- 07:00: scaffold run done. Decide-then-search EM: gemma 0.289, qwen 0.275, llama1b 0.150, mimir 0.120,
  llama3b 0.066. Calibration of the yes/no self-assessment: of the questions each model then got wrong,
  Mimir claimed to know 69%, Llama3B 88%, Gemma 11%, Qwen 1%, Llama1B 0% (said no to everything).
  Page data rebuilt (35 agg rows, 15 decision rows), walk clean, verdict extended, letter sentence updated.
- [x] Morning: pull results, sanity-check Mimir closed EM vs 9.6, write the page, update letter/CV.
