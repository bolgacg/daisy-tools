# Ideas, two loops (3 Sep 2026, late evening). Never delete; strike through when done or dropped.

## Loop 1: the study itself (what would make a language-model group nod)

Running tonight already: closed, retrieve (shaped query), agentic (model decides), retrieve-oracle
(subject as query = upper bound on asking), agentic-fewshot, closed-sc (5 samples, vote = test-time
scaling, the ad's topic 1 in miniature). Plus: replication of their five big models on the public
592, retrieval ceilings for three query formulations, reading fidelity (EM when the answer was in the
snippet vs not), and the call-decision 2x2 (called when wrong / silent when wrong / called when
right / silent when right, with call precision and recall).

Not yet built, ranked by value per hour:
1. **Lenient EM ("gold contained in prediction")** next to their strict EM. Separates knowledge
   failures from format failures ("i 1998" vs "1998", "Grundtvig" vs "N.F.S. Grundtvig"). Ten lines.
2. **Failure taxonomy with counts**, sampled 40 per condition per model and labelled by rule where
   possible: wrong entity, wrong year (off by how much), right entity wrong form, refused/hedged,
   copied the snippet title, answered in English, empty. The DAISY paper only gives anecdotes; a
   table with counts is exactly the missing piece.
3. **Query quality as its own measurement**: for the agentic runs, score the model's SEARCH query by
   whether Wikipedia's first hit is the gold subject page (we have Subject). "Can a 1B model ask?"
   independent of "can it read?".
4. **k and snippet-length sweep** on the best model (k = 1, 3, 5; 600 vs 1200 chars). Cheap with the
   cache; tells whether the 4096 context is the limit.
5. **Two-round agentic** (allow a second SEARCH after reading). Multi-hop in miniature.
6. **English Wikipedia as the tool** for the multilingual models: does the bridge language matter for
   Danish culture facts? One extra retrieval source, same harness.
7. **Confidence from logprobs** (llama-server returns them): does the token probability of the
   closed-book answer predict correctness, and does it predict the model's own decision to call?
   This is the calibration thread from the continuum and clinical demos, in text.
8. **Abstention scoring**: allow "ved ikke" and report EM at coverage (selective prediction curve).
   Ties to the group's safety interest (Galke).
9. **Mimir vs Llama, matched size**: Mimir 1B vs Llama 3.2 1B is the fair pair for "does Danish
   pretraining beat retrieval". Report that pair as the headline, the 3B/4B models as context.
10. **Cost accounting**: tokens and seconds per condition per model on the 1060; retrieval gain per
    extra token of context. A group that publishes distributed-training papers reads cost tables.
11. **Decide-then-act scaffold** (from the smoke test: Llama 1B never emits SEARCH, with or without
    examples). Two steps: first "Ved du svaret med sikkerhed? Svar ja eller nej", then search on nej.
    Separates the decision from the format; the free-form SEARCH line is a format hurdle for 1B models.
12. Not feasible by Sunday, name it in the letter as the next step: RL fine-tuning of the call
    decision (their GRPO recipe) on our logged rows; the 2x2 is the reward signal.

## Loop 2: the application and the page

Page (bolgacg.github.io/daisy-tools), built to DEMO-STANDARDS.md:
- Title as their question: "Does a lookup tool close the gap for a 1B Danish model?" Eyebrow: "a
  measured study on the Odense group's own benchmark and model, for the 4203 committee".
- First paragraph with three computed headline numbers, one per line: Mimir closed-book EM vs the
  paper's 9.6; the gain from the tool; the share of wrong answers the model chose to look up.
- Primer, five statements: what DAISY is, what a closed-book answer is, what retrieval adds, what
  "agentic" means here (the model chooses), what EM/F1 measure. Glossary open.
- The reader's own world before any control: their ad's three topics, their prompt (verbatim), the
  replication table of their five models, their Mimir Daisy number.
- Act 1, "How much of the canon do small models know?": chips per model, bars of closed-book EM/F1,
  the 70B line as reference. Handover: knowledge is thin, so can a tool supply it?
- Act 2, "Does looking it up help, and what limits it?": toggle query formulation (raw, shaped,
  oracle) to move the ceiling bar; achieved EM per model beside it; reading-fidelity split. Handover:
  the tool helps only when the model asks well and reads faithfully, so does it know WHEN to ask?
- Act 3, "Does the model know when it does not know?": the 2x2 as four tiles per model, click a tile
  to list its questions; a question browser (filter model, condition, outcome) showing gold, closed
  answer, query, retrieved titles, final answer.
- Model card: models, quantisation, decoding, prompt, scorer, hardware (GTX 1060, minutes per run).
- Failure pane: the taxonomy table; what this page does not test (fine-tuning, larger k, other
  sources, the 149 withheld questions, quantisation error).
- Coda: how it was built; every number generated by scripts/report.py; code and rows released.
- Spotlight walkthrough per 6.1; headless walk at 1536 and 390 px before Bo sees it.

Letter and CV:
- Replace the [[ARTIFACT]] block with three sentences carrying the headline numbers, and the 2x2
  as the sentence that matches "agentic behaviour": how often the model looked when it should have.
- The self-consistency row is the honest touch for topic 1 (test-time scaling): report it even if
  it does nothing, one sentence.
- The natural next step (their GRPO on our 2x2 as reward) is the sentence that shows the PhD plan.
- Statement of other qualifications: Danish (PD3) as a working language for a Danish-model group,
  Linux/GPU estate operation, founder track, the study itself as evidence of independent research.
- Pre-deadline note to Schneider-Kamp with the link, Saturday, only after Bo approves the text.

Risks and kill rules:
- Mimir closed-book EM far from 9.6 => check chat template (Gemma-4 style), max tokens, answer
  extraction, before trusting anything else.
- If the runs do not finish cleanly by Saturday evening, the page is not published and the letter
  loses the artifact block (Bo's rule).
