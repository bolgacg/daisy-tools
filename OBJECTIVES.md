# Objectives (Bo, 4 Sep 2026, 12:30). The race framing.

## The goal in one line
Build something on their own field that beats what they have on their own terms, with close to no downside,
so that the group would want to use the method and the tool. Deadline for the application: Sun 7 Sep 23:59.

## What "same field, same terms" means here
1. Calibration A, closed book: our numbers must reproduce theirs before anything else counts.
   - Their five big models: reproduced from their prediction files with their scorer (done; same ranking).
   - Mimir: paper 9.6 EM (741) vs ours 5.6 (592, Q8, community llama.cpp). OPEN. Job 010 runs the official
     transformers path with full weights; then we know whether the gap is our copy, their harness or the subset.
2. Calibration B, tool use: they have published NO tool or retrieval number on DAISY. Their tool paper is
   Prolog on GSM8K. So there is no baseline of theirs to match; ours is the first. Record this as a fact,
   not a claim. (If Bo wants: replicate the Prolog paper's inference on GSM8K, one day, not for this deadline.)
3. The race: same 592 questions, same scorer, same prompt; every condition reported with the standard
   academic metric names (lit/METRICS-AND-TERMS.md) AND the cost axis they would care about: tokens per
   question, retrieval calls per question, seconds per question on one GTX 1060. Accuracy is the
   compression ratio; cost is the bitrate; fidelity is reading fidelity; the decision quality is the
   rate-distortion knob (selective prediction: coverage vs selective risk).
4. Best in the field: place our numbers next to PopQA/NQ/TriviaQA adaptive-retrieval results and the
   "small model + retrieval beats huge model" headline results (lit/SOTA-COMPARABLES.md), stating every mismatch.

## What would count as winning
- A Mimir-based system that beats every stronger closed-book model on DAISY at lower cost than the
  4B agentic models: candidate = asker/reader split (a 3-4B model or a rule writes the query, Mimir reads;
  job 020) plus a confidence gate (job: logprob runs + scripts/confidence_gate.py) so lookups happen only
  when needed. Report: EM, lenient EM, F1, calls per question, tokens per question, seconds per question.
- If Mimir cannot win, say which model does and why, with the same table.

## Queue on the box (systemd daisy-queue, ~/queue): 010 official Mimir; 020 asker/reader hybrids;
## 030 k and snippet-length sweep; 040 English Wikipedia; 050 remaining logprob runs. qstatus.sh shows state.

## Literature agents (writing into lit/): GROUP-PAPERS.md (hidden apples in their papers), METRICS-AND-TERMS.md
## (correct vocabulary, comparables), SOTA-COMPARABLES.md (best in field, Danish QA, cost conventions).

## Then: rebuild RESULTS/page with the canonical metric names and the cost axis; update letter and CV; publish.
