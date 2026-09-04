# What DFM and the Odense group are optimising for

Researched 4 Sep 2026 for the 4203 application (deadline Sun 7 Sep). Question from Bo: "Figure out what
these guys are trying to optimize for. Why are they building their own Danish LLM? What is the centre trying
to achieve, and what is the professor trying to achieve?" Sources are listed at the end with dates; every
quote is verbatim except that dash punctuation in the originals has been replaced by commas or full stops.

## The answer in one line

DFM optimises for a Danish language stack that the Danish state can legally own and run itself: open weights,
data that is provably permissible, benchmarks that measure Danish rather than English, and public sector
use. The Odense group optimises for doing that with the smallest model and the least compute that still
matches the frontier on their own Danish benchmarks, and for making the model's reasoning auditable.

## 1. DFM's stated objectives, in their own words

### 1a. Don't get left behind; don't depend on foreign providers

- 2023 position paper (arXiv 2311.07264, Enevoldsen, Hansen, Nielsen and 10 others, AU, Alexandra, Alvenir):
  "smaller languages risk falling behind due to high training costs and small incentives for large companies
  to train these models. To combat this, the Danish Foundation Models project seeks to provide and maintain
  open, well-documented, and high-quality foundation models for the Danish language."
- Same paper: "Developing Danish foundation models by a public institution becomes imperative due to the
  limited incentive for large tech companies to invest in languages spoken by smaller populations."
- Same paper on why the tasks differ: "Use cases such as healthcare services or citizen-state interactions
  will have high priority, while assistive technologies, e.g., programming, will be less central for national
  models." And: "National use cases also require different restrictions relating to privacy and governance,
  which necessitate local solutions without the need to send sensitive data to foreign service providers."
- foundationmodels.dk (Sep 2026): "Sprogmodeller er blevet kritisk infrastruktur, men mindre sprog som dansk
  risikerer at blive efterladt." English version: preventing smaller languages like Danish from being
  "left behind" as language models become critical infrastructure. Headline: "Vi bygger fundamentet for
  dansk AI."
- OECD.AI policy entry (initiative 3 of Denmark's national AI strategy, start 2024): the rationale is that
  "most advanced language technologies are built for English or controlled by large foreign firms, leaving
  smaller languages and local institutions at a disadvantage." Runs on UCloud, the SDU-hosted national
  research cloud connected to European supercomputers.
- Schneider-Kamp, SDU news, 20 Aug 2026: "Det betyder, at vi kan være datasuveræne. At vi kan være
  uafhængige af amerikanere og kinesere." And on local inference: "Så er det kun den strøm, du bruger på din
  maskine. Og så er der ikke nogen data, der bliver sendt ud."
- Ordbogen press release, 14 Aug 2026 (title: "en digital fremtid, vi selv bestemmer over"). Peter Revsbech,
  Ordbogen CEO: "Vi har bevist, at man ikke behøver være en techgigant for at bygge AI i verdensklasse."
  TV2 Fyn, 18 Aug 2026, Revsbech: with Mimir "digital suverænitet for Danmark og EU er en realistisk plan."

The ministry says the same thing from the policy side. Minister Caroline Stage Olsen, Dansk Erhverv
magazine, 2025: "Hvis stikket bliver trukket, står vi i en enormt alvorlig situation." Altinget, 16 Jun 2025:
"Det vil ikke være klogt at sige, at vi aldrig nogensinde skal have et samarbejde med eksempelvis amerikanske
eller kinesiske virksomheder." The government's separate digital sovereignty pot is 80 million DKK for
2026 to 2029 (Digitaliseringsministeriet press release, 28 Aug 2025). The language-model line is not paid
from that pot.

### 1b. Legally clean, consented data

- Mimir paper (arXiv 2608.13517, Aug 2026): DFM "adheres to a philosophy of using exclusively permissible
  and, whenever possible, openly licensed data." Their definition of permissible: "excluding data containing
  personal information or copyright infringement and including data that is either openly licensed, made
  available by agreement, or allowed by the European Union's text and data mining exception for research
  institutions."
- Dynaword paper (arXiv 2508.02271, Enevoldsen et al., LREC 2026) names the scar tissue: a Danish encoder
  was "removed following threats of legal action" and the Nordic Pile "was never released, presumably due to
  copyright issues." Their three tiers: replicable, open access, and "openly licensed, enables resharing,
  reuse, and modification." Only the third tier counts for them.
- Dansk Sprogmodel Konsortium principles (Dansk Erhverv page, founding parties Alexandra, IBM Danmark, Dansk
  Erhverv, 70+ members): models "open source, freely accessible, and commercially applicable"; training on
  "owner-approved datasets with personal information filtered; data remains within EU."
- Media data declaration, 9 Apr 2025 (DSK with DPCMO, the press publishers' collecting society). Jens Kaas
  Benner, Alexandra: "Muligheden for frikøb af data fra de danske medier er en afgørende faktor for, hvor
  hurtigt vi kan udvikle uafhængige, åbne, danske sprogmodeller." Minister: Denmark works with language
  models "på den danske måde, hvor vi går ansvarligt til værks."
- Schneider-Kamp, Ordbogen release, 14 Aug 2026: "Vi har vendt opskriften på hovedet. I stedet for at skrabe
  data fra internettet har vi kurateret og syntetisk genskabt data, så Mimir er trænet 100 procent
  ansvarligt, uden at gå på kompromis med ydeevnen."
- The state's data side: Digitaliseringsstyrelsen, 2 Dec 2024, 21.1 million DKK for 2024 to 2027 to make
  about 300 billion tokens (about 200 billion words) of Danish text from Rigsarkivet, Det Kgl. Bibliotek,
  Folketinget and public publications available for training.

### 1c. Danish language and culture quality, measured on Danish benchmarks

- 2023 paper: models trained on mostly English "inherently carry assumptions and cultural biases that may
  not seamlessly transfer between languages and cultures." Their evidence then: on ScandEval "multilingual,
  and even monolingual Norwegian models, outperformed their Danish counterparts."
- 2023 paper aims 2 and 3: "To extensively validate foundation models for Danish in a representative set of
  tasks" and "To maintain a high standard of documentation of models such as model cards and datasheets."
- Bolette Sandford Pedersen, KU, grant release 2 Dec 2024: "sprogmodellerne evalueres ud fra den kulturelle
  og samfundsmæssige sammenhæng."
- digst.dk language technology page: Denmark is "et lille sprogområde med et komplekst sprog", which is
  the market-failure argument for state funding.
- The Odense benchmarks follow directly: DAISY (Danish Culture Canon 2006), DaLA (real Danish writing
  errors), IFEval-Da, Multi Wiki QA, Hellaswag-da.

### 1d. Open by design

- 2023 paper aim 4: "To open-source not only the models but also all components required for reproducibility
  such as pre-processing, training, and validation code."
- foundationmodels.dk: "Åbenhed som grundprincip." "All models, datasets, and research are freely
  available, enabling transparency, reproducibility, and broad access."
- Grant release (ritzau, 2 Dec 2024): "Det er hensigten at gøre basis- og finjusterede modeller mere
  tilgængelige med open source via R&D-platformen, så de f.eks. også kan benyttes til kommerciel brug."
- Mimir: Apache 2.0 on Hugging Face; training framework released on top of Sapient's HRM-Text code.

### 1e. Public sector and SME use cases, a "sandbox"

- Grant, 2 Dec 2024: 30.7 million DKK total from Digitaliseringsministeriet. 20.7 million for 2024 to 2027
  to build "a secure R&D platform for training, fine-tuning, evaluation and maintenance of foundation
  models"; 10 million from the 2025 research reserve. Use cases in "offentlig forvaltning, uddannelses- og
  sundhedssektor samt små og mellemstore virksomheder." Plus "en innovativ og åben 'sandkasse' udformet med
  henblik på løbende samarbejde om finjusteringer og tilpasninger af basismodellerne."
- Schneider-Kamp in that release: "Ved at tænke strenge sikkerhedsprotokoller med kollaborativ og
  brugerdrevet fleksibilitet stiler DFM mod at udnytte det fulde potentiale af AI for at tjene
  forskelligartede danske samfundsmæssige behov."
- foundationmodels.dk claims "20+ Industry Use Cases" with Alvenir, Ordbogen.com, Agency for Digital
  Government, Lex.dk and the TEXT research programme named as adopters.
- Ordbogen release: schools, hospitals, agencies and businesses should be able to run Danish-built AI while
  sensitive data stays in Denmark.

### 1f. Efficiency and energy

Not in the DFM mission text. It appears only in the Mimir communication, and there it is central:
Schneider-Kamp (SDU, 20 Aug 2026): "Vi har ikke så meget data, og slet ikke dansk data. Men fordi vi ikke
har brug for så meget data, så kan vi pludselig være med alligevel." And: "ChatGPT er jo 1.000 gange større.
Men vi kan konkurrere med de bedste modeller på den størrelse, som de kan lave." The paper's own framing:
"small, capable and fully permissible models, with both low training and inference requirements." No energy
figures are published anywhere (paper, model card, or press).

### 1g. Who pays and who runs it

| Item | Amount | Years | Source |
|---|---|---|---|
| DFM R&D platform (Alexandra, SDU, AU, KU) | 20.7 M DKK | 2024 to 2027 | Digitaliseringsministeriet, 2 Dec 2024 |
| DFM research and innovation, research reserve | 10 M DKK | 2025 | Uddannelses- og Forskningsministeriet, 1 Nov 2024 |
| Danish text data made available (Digitaliseringsstyrelsen) | 21.1 M DKK | 2024 to 2027 | digst.dk, 2 Dec 2024 |
| Digital sovereignty pilot pot (not language models) | 80 M DKK | 2026 to 2029 | Digitaliseringsministeriet, 28 Aug 2025 |
| MIST (Galke, AI safety of LLM agents) | not public | from 2026 | Novo Nordisk Foundation |

Mimir's acknowledgement names the funder as "the Ministry of Science, Higher Education and Digital
Affairs", i.e. the merged ministry after the 2025 reshuffle. Compute for Mimir was 8 B200 GPUs for under
three weeks; the paper does not say whose. Ordbogen bought its own NVIDIA machine for about 3 million DKK
in Nov 2025 for Chat.dk (DI Business, 17 Dec 2025).

## 2. Why build your own instead of fine-tuning Llama or Gemma

### 2a. First fact: DFM does both, and Mimir is the from-scratch line winning an internal race

DFM's Hugging Face organisation carries two generative lines. Munin 1.0 (June 2026) is "existing base
models post-trained for Danish and English": munin-apertus-8b, munin-qwen3.5-9B, munin-ministral3-8B. Mimir
(Aug 2026) is trained from scratch. In the Mimir paper's Danish table, Mimir 1B scores 56.8 against
Munin-Apertus 8B 45.6, Munin-Mistral 8B 45.6, Munin-Qwen 9B 43.9. The paper's sentence: "Mimir displays
superior performance on the Danish benchmarks" while being 8 to 9 times smaller. So the question "why not
fine-tune" has been run as an experiment inside DFM, on DFM's own benchmark suite, and the from-scratch
line won. That is the strongest argument they have, and it is an empirical one.

### 2b. Their arguments as they state them

1. Permissibility is inherited. A fine-tune of Llama, Gemma or Qwen carries the base model's undisclosed
   pretraining data. Only a from-scratch model can be, in their words, a "fully permissible base model."
   Apertus (Swiss, fully open data) is the one exception and is the base of one Munin variant; it still lost
   to Mimir on Danish.
2. The frontier recipe is closed to them. Mimir intro: "Current development is largely driven by a
   'monolithic recipe' consisting of massive, multi-stage pipelines and training on exorbitant volumes of
   data," and current LLM development "relies on massive, often non-permissible datasets, creating a high
   barrier for researchers committed to open-source and ethically sourced data."
3. Data efficiency turns Danish's weakness into a non-issue. HRM-Text (Sapient, arXiv 2605.20613, May 2026)
   trains on instruction-response pairs with a task-completion objective and skips raw-text pretraining;
   Sapient's 1B used about 40B unique tokens and a claimed 1,500 dollar budget. Mimir: the framework "enables
   focusing on post-training data during the initial training phase, thereby facilitating the creation of a
   viable base model." Schneider-Kamp's spoken version is the "we don't need so much data" quote above.
4. Small enough to run locally means no data leaves and less electricity. This is the sovereignty claim
   made concrete: a 1B model runs on a laptop or a municipal server.
5. Danish culture in the model, not bolted on. DAISY, DaLA and Lærebogen exist so that the training and
   the test both come from Danish sources.

### 2c. The counter-argument (the "80 percent as good own thing")

- DFM's own state-of-the-art list disagrees with the headline. The Hugging Face collection "State-of-the-art
  Danish Models", built from EuroEval Danish NLG (Nov 2025), lists Mistral Small 24B, Gemma 3 27B, Gemma 3n
  E4B and Gemma 2 9B as the best generative models for Danish. No Danish-built model is on it. Whether Mimir
  has been run through EuroEval could not be verified (the leaderboard page is script-rendered). If the
  standard is "best model a Danish agency can download today", the answer is still a foreign open-weight
  model, and the DFM sandbox exists precisely to fine-tune those.
- The 1B size is a budget consequence dressed as a design goal. Sapient's own limitation: "demonstrating
  similar efficiency gains at larger model scales remains in the scope of future work." Mimir's future work:
  "investigating scaling behavior of HRM models." Nobody yet knows whether HRM holds up at 4B or 8B.
- The Danish win is measured on a suite the group co-designed. Of the 10 Danish benchmarks, DaLA, GEC-DaLA
  and DAISY are the Odense group's own, IFEval-Da, Multi Wiki QA and Hellaswag-da are DFM adaptations. The
  competitors never saw DaLA-style corruptions in training; Mimir trained on 8.32B tokens of Lærebogen
  (2.08B tokens repeated 4 times, 11.8 percent of the corpus), a Danish instruction and knowledge set the
  paper does not describe beyond its size.
- Assistant quality is admitted to be behind. Paper: "the capabilities as an assistant are still limited
  compared to the state of the art." Press (viden.ai and TV2 Fyn): Mimir "kan ikke bruges i en webchat
  endnu, da det er en forskningsmodel og proof-of-concept." Ordbogen's actual product, Chat.dk, runs
  "Odin-LLM", an open-source model "trænet og finjusteret specifikt til dansk", i.e. the fine-tune route.
- Continued pretraining is cheaper and was the Danish default until 2026. SnakModel (ITU, arXiv 2412.12956)
  took Llama2-7B and continued pretraining on 13.6B Danish words. Dynaword's own experiment reports a 5.9
  percent relative gain from continual pretraining of Gemma 3 1B on Dynaword versus Gigaword, and 26 percent
  from scratch, but both at 1B and both against a Danish baseline, not against Gemma itself.
- The state's own 2023 analysis did not pick this path. "Sprogmodeller i Danmark" (for KL, ATP and
  Digitaliseringsministeriet, Sep 2023, 125 pages) laid out four scenarios: 0 "Afvent, men regulér
  decentrale projekter", 1 "Dansk minimumsmodel", 2 "Autorisationsordning", 3 "Fællesoffentlig
  infrastruktur", and "afholder sig fra at konkludere løsningsrummet." Its strategy seminar summarised
  scenario 3's purpose as "suverænitet og kontrol samt et konkurrencedygtigt alternativ til big tech" and
  scenario 1's as "fastholde det danske sprog og fremtidssikre, at Danmark kan stå alene samt har ejerskab
  over essentiel teknologi." DFM's 30.7 million is a scenario 1 budget with scenario 3 rhetoric.
- The 80 percent answer, stated plainly: for a Danish agency that needs a chat assistant today, a fine-tuned
  Gemma or Mistral is better, and DFM ships those (Munin). Mimir is the proof that a permissible,
  from-scratch, locally runnable model is not hopeless at 1B. Its value is the recipe and the legal position,
  not the model.

## 3. What Mimir specifically optimises

### 3a. Architecture: HRM, and why

- Hierarchical Reasoning Model (Wang et al. 2026, Sapient Intelligence): two Transformer modules, a slow
  high-level H and a fast low-level L, iterated over the same input for H_cycles times (L_cycles plus 1)
  steps, with additive state injection. Mimir uses 2 H-cycles and 3 L-cycles. Effectively unbounded compute
  depth at bounded parameter count.
- HRM-Text (Sapient, May 2026): task-completion objective, "optimize the NLL of the response conditioned on
  the instruction", PrefixLM masking, no raw-text pretraining. Sapient motivation: "The current pretraining
  paradigm for large language models relies on massive compute and internet-scale raw text, creating a
  significant barrier to foundational research."
- Mimir's stated reason for choosing it is the one quoted in 2b (focus on post-training data from step one).
  The paper does not compare HRM to a same-budget standard Transformer. That comparison is absent.
- Size: 1.3B non-embedding plus 0.4B embedding parameters, hidden 1,536, 12 heads per layer. Gemma 4
  tokenizer and Gemma 4 chat template from scratch.

### 3b. Data

- 161 datasets, 70,479,308,606 tokens per epoch. 68.5 percent English, 24.7 percent Danish, 6.4 percent
  bilingual. "6 out of 8 categories are entirely English"; Danish sits in instruction-following and
  knowledge.
- Top three: Sapient mega-repository 11.92B tokens (16.9 percent; 107 sub-collections of Flan, Platypus,
  tasksource, "dominated by multiple-choice classification tasks"), Lærebogen 8.32B (11.8 percent, at 4x
  repetition), OpenMathInstruct-2 6.60B (9.4 percent).
- Processing: 66 percent simply reformatted public data, 17 percent curated and reformatted (Sapient), 11
  percent synthetically generated and audited. 70 "transplant datasets" (75M tokens) are "synthetic
  recreations of English instruction tasks ... replacing original Sapient data that was non-compliant with
  the DFM philosophy."
- Memorisation audit: 50-token prefix attacks across four categories; verbatim spans of 50 or more tokens in
  0.00022 to 0.015 percent of documents; "no high-priority copyright findings."
- Compute: 1.65M steps, 8 NVIDIA B200 (180 GB), just under 3 weeks, about 1.1 s per step. No GPU-hour or
  energy total is given.

### 3c. The 20 benchmarks and what each measures

English (7): BoolQ (yes/no reading), Winogrande (coreference), Hellaswag (commonsense completion), MMLU
(multitask knowledge), ARC-C (science reasoning), DROP (discrete reasoning over paragraphs, F1), GovReport
(long summarisation, ROUGE-1). Math and code (3): GSM8K, MATH, HumanEval. Danish (10): Angry Tweets
(sentiment), DaLA (error detection, F1), GEC-DaLA (error correction, exact match), PIQA-da (physical
commonsense), DAISY (culture QA, exact match), Multi Wiki QA (multi-document QA, exact match), WMT24++ EN-DA
(translation, chrF), Nordjylland News summarisation (chrF), IFEval-Da (instruction following), Hellaswag-da.

Results: English average 69.0 (beats all 1B models; wins BoolQ, Winogrande, DROP outright); Math and code
64.1 (36.7 percent over HRM-Text's 46.9; behind Gemma 4 E2B); Danish 56.8 (wins DaLA, GEC-DaLA, Multi Wiki
QA; close on Nordjylland News). Greedy decoding, temperature 0. On DAISY the paper reports 9.6 exact match
(see GROUP-PAPERS.md section 3.2 for why our closed-book run gives 5.6 on 592).

What the suite says about their priorities: half the Danish suite is grammar, error correction and
instruction following, which is Ordbogen's product territory (grammar checking, dictionaries, Chat.dk), and
DFM's public-sector territory (citizen letters). Culture knowledge (DAISY) and translation are one slot each.
Nothing on retrieval, tool use, long context, or speech.

### 3d. What they say is future work

Verbatim from the paper: "investigating scaling behavior of HRM models"; exploring "reinforcement learning,
which is yet unexplored for this architecture"; continuing "dataset development to achieve full openness
regarding licensing." Admitted gaps: math and code behind Gemma 4; assistant capabilities limited; model card:
"trained on Danish and English data only", "will likely have poor performance on other languages", no safety
alignment.

## 4. The Odense group's agenda and the PhD call

### 4a. The record, Aug 2025 to Aug 2026 (details in GROUP-PAPERS.md)

- Benchmarks that measure Danish the way it is actually used: DaLA (Dec 2025, LREC 2026; 14 corruption
  functions from real error statistics), DAISY (Jan 2026; 741 QA on the Culture Canon), SommBench (Mar
  2026; expert domain, 8 languages), IFEval-Da, Dynaword (with AU).
- Models under a legal and compute constraint: Mimir (Aug 2026).
- Making training cheaper and more distributable: DeToNATION (AAAI 2026, decoupled network-aware training
  across ordinary internet nodes), FlexMoRE (federated, rank-heterogeneous experts), the BitNet 1.58-bit
  trio (2024 to 2025), Axon DSL, BrainSurgery.
- Making reasoning auditable: "Training Language Models to Use Prolog as a Tool" (ACL Findings 2026;
  Mellgren, Schneider-Kamp, Galke). Motivation verbatim: "reasoning traces are not always faithful";
  Prolog gives "precise and auditable reasoning traces, i.e., composed of explicit facts and rules"; for
  safety-critical use "textual reasoning traces that are potentially unfaithful do not serve this purpose."
  Finding: reward for correctness alone makes the model "delegate reasoning to natural language and use
  Prolog only for the final computation", which they call "a clear instance of reward hacking." Two agentic
  inference modes (internal loop up to 20 turns; independent with context reset). Limitations they name:
  "limited to elementary arithmetic reasoning problems", "a single tool (SWI-Prolog)", "one reinforcement
  method (GRPO)"; open problem "generalization to richer domains."
- Safety and interpretability line (Galke): memorisation propensity, activation-oracle calibration,
  PsychoSafe, Arbiter Agent, emergent languages in agent populations, guarded query routing.

### 4b. The two people

- Peter Schneider-Kamp: professor, IMADA; roots in termination analysis and logic programming; leads SDU's
  DFM part; also CIO of Ordbogen A/S, which runs Chat.dk (Danish-hosted assistant, free for schools, API sold
  to municipalities) and bought a 3 million DKK NVIDIA machine in Nov 2025. His DI quote: "Vores sprogmodel
  er målrettet det danske marked og er baseret på dansk viden, søgehistorik og dansk kultur." Read his agenda
  as: a Danish model that a Danish company can ship without legal exposure, plus logic-programming-flavoured
  tool use so the model's answers can be checked.
- Lukas Galke Poech: associate professor, leads the AI Safety and Interpretability Lab, MIST project (Novo
  Nordisk Foundation, "scalable mechanistic interpretability for safe and trustworthy LLM agents"). His
  statement: "My research advances AI safety by understanding how and why AI models behave the way they do,
  and by developing methods to keep that behavior legible and controllable." His named central tension:
  "auditability vs. accuracy." Also listed on his site: the DFM alignment workstream and "DFM Mimir v1:
  multilingual model development emphasizing European AI sovereignty."

### 4c. The 4203 call, read against the record

The ad (posted 17 Aug 2026, closes 17 Sep, start 1 Oct 2026, "under the umbrella of the Danish Foundation
Models initiative") wants "development of advanced language models and derived use cases" on one or more
of: "LLM customization and test-time scaling", "Agentic behaviour and tool use", "Multi-modality and
interactivity". Background wanted: deep learning models, mathematical foundations of ML, "optimal deployment
of AI systems"; Python required, Rust or C++ a plus.

Mapping to what they have and what they lack:

| Call topic | What exists | The gap they are hiring for |
|---|---|---|
| Customization and test-time scaling | Mimir base; HRM has H and L cycle counts as a natural inference-compute knob; original HRM paper had adaptive computation time | Nothing measured: the paper trains and evaluates at fixed 2/3 cycles; no accuracy-versus-compute curve; RL for HRM unexplored |
| Agentic behaviour and tool use | Prolog tool paper, PrologMCP (Royal Holloway group, Jun 2026) as a standard interface; guarded query routing | One tool, one dataset, one RL method; no retrieval, no multi-tool, nothing in Danish, nothing on Mimir |
| Multi-modality and interactivity | DFM speech line (CoRal, Hviske, at AU and Alexandra); nothing multimodal from Odense | A Mimir-class model that sees or listens; "interactivity" reads as the sandbox and Chat.dk |

What they measure: accuracy on their own Danish suite plus the standard English set, always at greedy
decoding; tokens and compute in the HRM-Text sense (fewer training tokens, fewer GPUs); and, in the tool
line, whether the reasoning is auditable (share of answers computed in Prolog versus prose). What they do
not yet measure: inference cost per answer, retrieval calls, energy, calibration of "I don't know". That is
the open lane for Bo's study (OBJECTIVES.md, the cost axis and the confidence gate).

## 5. Plain-language answer, to read aloud

They are building their own Danish model because the models everyone uses are American or Chinese, were
trained on text nobody was asked about, and treat Danish as an afterthought. The centre's job, paid for by
the Danish state with about thirty million kroner, is to make sure Denmark owns a working language stack:
the training data, the model weights, the tests, and the code, all open, all legal, all runnable inside a
Danish hospital or town hall without sending anything abroad. They also fine tune the big foreign open
models, and for a chat assistant today those are still better. The point of building one from nothing is
that it is the only way to promise that nothing in it was stolen, and they want to show the recipe works.

The professor is optimising for something narrower and sharper. He wants the smallest model that matches the
big ones on Danish, trained in three weeks on eight graphics cards, so that a school or a small company can
run it on its own machine. He co owns a Danish dictionary company that sells grammar tools and a Danish chat
service, so grammar correction and Danish writing are the tests he cares about most. His background is in
logic, and his newest line teaches models to hand their reasoning to a logic program so a human can check
it. The PhD he is hiring for is meant to push exactly those two things: making a small model think longer
when it needs to, and making it call tools instead of guessing.

## 6. Three questions a sharp outsider should ask, with best-guess answers

1. Your own state-of-the-art list for Danish is Mistral 24B and Gemma 27B. Who will run Mimir instead, and
   for what?
   Best guess: nobody for chat yet, and they would say so. The intended users are narrow, high-volume Danish
   tasks where data cannot leave the building: grammar and error correction, classification, extraction,
   form letters. Ordbogen's grammar products are the obvious first deployment. Mimir v1 is a recipe proof;
   the real product is v2 at a larger size if HRM scales.

2. How much of the Danish win comes from benchmarks you wrote and data only you trained on?
   Best guess: they would point to the memorisation audit and to the English wins on public benchmarks. The
   honest answer is that DaLA, GEC-DaLA and DAISY were built by the same group, the competitors never saw
   DaLA-style corruptions, and Lærebogen at four repetitions is 12 percent of the corpus with no public
   description. An outsider should ask for EuroEval Danish numbers, which are the consortium's own neutral
   yardstick, and for the DAISY score with and without Lærebogen.

3. What does test-time scaling mean for an HRM, and did you measure it? And what does one answer cost?
   Best guess: not measured. The architecture lets you run more H and L cycles at inference, which is a real
   knob the paper never turns; adaptive computation existed in the original HRM. Nor does the paper give
   inference latency, tokens per answer, or joules, despite the energy claim in the press. The PhD topic
   "test-time scaling" is that missing curve. For our study this is the exact gap: accuracy against seconds
   and calls per question on one consumer GPU, with a gate that decides when to look something up.

## Sources (fetched 4 Sep 2026)

- foundationmodels.dk and /da/ (mission, partners, use cases); /news/2026/08/14/mimir-1-release-note.html
- DFM position paper, arXiv 2311.07264 (Nov 2023), read from PDF
- Dynaword, arXiv 2508.02271 (Aug 2025, LREC 2026)
- DFM Mimir v1, arXiv 2608.13517 v2 (Aug 2026); Hugging Face danish-foundation-models/DFM-Mimir
- HRM-Text, arXiv 2605.20613 (Sapient Intelligence, May 2026); github.com/sapientinc/HRM-Text
- SDUs DAISY, arXiv 2601.19930 (Jan 2026); DaLA, arXiv 2512.04799 (Dec 2025); SommBench, arXiv 2603.12117
- Training Language Models to Use Prolog as a Tool, arXiv 2512.07407 (ACL Findings 2026); PrologMCP,
  arXiv 2606.14935
- SnakModel, arXiv 2412.12956 (ITU, Dec 2024)
- SDU news: "Danmark har førertrøjen på i kapløbet om små sprogmodeller", 20 Aug 2026; "Digitaliserings-
  ministeriet bevilger samlet 30,7 millioner", 2 Dec 2024
- Ordbogen A/S press release via Ritzau, 14 Aug 2026; TV2 Fyn, 18 Aug 2026; viden.ai on Chat.dk, 13 Dec
  2025; DI Business "Trio hentede selv supercomputer i Holland", 17 Dec 2025
- Alexandra Institute via Ritzau: grant release 2 Dec 2024; media data declaration 9 Apr 2025; "Nye midler"
  1 Nov 2024 (alexandra.dk itself was unreachable from here)
- Version2, 2 Dec 2024 (platform and sandbox); Version2 opinion by Markus Hens, EY, 8 Jun 2025 (Denmark
  talks sovereignty, Germany builds it)
- OECD.AI policy initiative "Secure platform for developing transparent Danish language models"
- digst.dk: "Dansk sprogteknologi"; "Danske tekster gøres klar til kunstig intelligens", 2 Dec 2024
- Dansk Erhverv: DSK principles page; magazine 02/2025 interview with Caroline Stage; Altinget 16 Jun 2025;
  Digitaliseringsministeriet 80 M DKK release, 28 Aug 2025
- KL, ATP, Digitaliseringsministeriet: "Sprogmodeller i Danmark, en analyse af mulige strategiske valg og
  scenarier", Sep 2023 (125-page PDF, read locally)
- Hugging Face collections: danish-foundation-models "State-of-the-art Danish Models" (EuroEval Danish NLG,
  Nov 2025); Munin 1.0 (Jun 2026)
- lgalke.github.io (research statement, MIST); SDU job ad 4203 (positions/ad-4203.json, posted 17 Aug 2026)
- Not reachable from this machine: alexandra.dk, chc.au.dk, digmin.dk PDF "Strategisk indsats for kunstig
  intelligens", ida.dk, techsavvy.media, cybernews.com, euroeval.com leaderboard (script-rendered). Nothing
  above depends on them alone.
