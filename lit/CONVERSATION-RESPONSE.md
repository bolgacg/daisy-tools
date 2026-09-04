# Response to the recorded conversation of 4 September 2026 (29 minutes, English, three transcription passes)

Transcription: faster-whisper small (laptop), large-v3 on the box CPU, and a large-v3 GPU pass; the passes agree on
every passage quoted below. Timestamps are minutes:seconds into the recording. Research behind the answers:
lit/WHAT-THEY-OPTIMISE-FOR.md and lit/HOW-AI-ANSWERS-AND-GEO.md (both with sources), plus our own results.

## What was addressed to me
1. [2:24] Figure out what these guys are trying to optimise for. Why are they building their own thing?
2. [3:03] What is the centre trying to achieve, and what is the professor trying to achieve?
3. [8:21] Tell me exactly how the tools we created work, and what mechanism the lookup uses.
4. [13:23] Respond to what is addressed to me, and come up with my own questions from the conversation and answer them.
5. [22:24] Three ways AI answers come about (cached, live search, training memory): correct me if I am wrong.
6. [24:55] How does AI engine optimisation work; how do people structure websites to show up in AI engines?
7. [21:11, Olha] When it searches, does it separate scientifically proven sources from opinion sites?
8. [25:03, Olha] Can I make it use only scientific sources, and does that help?
9. [25:55, Bo's claim] Providers default to shallow answers to save compute; only forcing ("check academia") makes it dig.

## 1 and 2. What they optimise for, and why build their own
The Danish Foundation Models initiative exists because the models everyone uses are American or Chinese, were trained
on text nobody consented to, and treat Danish as an afterthought. The Danish state pays about 30 million kroner for a
language stack Denmark can legally own and run: open weights, provably permissible data, Danish-specific tests, and
public sector use inside a hospital or a town hall without sending anything abroad. The professor said it himself:
"data sovereign, independent of Americans and Chinese". They do both things you guessed: they fine-tune foreign open
models (their Munin line) and they train Mimir from nothing. Their argument for from-nothing is that a fine-tune inherits
the base model's unconsented pretraining, so only a from-scratch model can promise nothing in it was taken. Your
"80 percent as good but our own" instinct is right and they know it: their own list of the best Danish models is still
Mistral 24B and Gemma 27B, Mimir cannot yet serve a web chat, and the dictionary company's real product runs a fine-tuned
foreign model. Mimir v1 is a recipe proof at the size their budget allowed (eight GPUs, three weeks).

The professor is narrower and sharper. He wants the smallest model that matches the big ones on Danish so a school or a
small firm can run it locally. He is also chief technology officer of Ordbogen, the dictionary and grammar company behind
Chat.dk, so grammar correction and Danish writing are the tests he cares about most; half of Mimir's Danish test suite is
grammar and instruction following, and three of the benchmarks are his group's own. His background is logic, and his
newest line makes models hand their reasoning to a Prolog program so a human can audit it. The PhD he is hiring for
targets exactly the gaps his own papers leave open: making a small model think longer when it needs to (test-time
scaling, a knob his architecture has and the paper never turns), and making it call tools instead of guessing. Nothing
in any of their papers measures retrieval, tool use on Mimir, cost, latency or energy, despite the energy claims in the
press. Those gaps are where our study sits.

Three questions a sharp outsider should put to them: who will run Mimir instead of Gemma 27B, and for what; how much of
the Danish win comes from benchmarks they wrote and a textbook corpus only they trained on; and what one answer costs in
seconds and what test-time scaling means for their architecture. The third is our lane.

## 3. How the tools we built work, exactly
Nothing here is a trained model. Every "tool" is a few hundred lines of Python between the question and the model, and
the model only ever sees text.

The lookup is Danish Wikipedia's public search interface, the one behind the site's search box. Given a search string
it returns the three best-matching article titles; a second call fetches the first paragraphs of each, up to 900
characters. Those paragraphs are pasted above the question under the heading "Baggrundsviden fra dansk Wikipedia" and
the group's own prompt follows unchanged. It does not search for keywords inside the text and does not cut sentences
around keywords: the model gets the introductions whole and must find the answer. Every result is cached on disk.

The "shitty tool" is a rule for the search string. Wikipedia finds nothing for a whole question because every word must
match, so the rule strips question words, keeps names and numbers first, and drops words from the end until something
comes back. The answer is inside the fetched paragraphs 40 percent of the time; Mimir then answers correctly 32.8
percent of the time (26.5 on the port we used overnight).

The "better tool" at 60 percent is not a tool. It is the oracle query: the name of the canon work, which the benchmark
stores in a hidden field no model can see. It fetches the right page 79 percent of the time. It tells us what asking
well is worth; it cannot be deployed.

The agentic tool tells the model it may write one line "SEARCH: <words>" or answer directly. Gemma 3 4B and Qwen 2.5 3B
write their own queries, land on the right page about half the time, and reach 40 percent, above the rule query. Mimir,
Llama 1B and Llama 3B never write the line. A decide-then-search variant asks "do you know this for sure?" first and
searches on no; it shows the models' self-knowledge is poor: Mimir says yes on 69 percent of the questions it then gets
wrong. The split that moved the record: one model writes the query, Mimir reads. Mimir reading Qwen's queries scored
38.2 on the old port, and the rerun through the correct implementation is in progress.

The fix that made the numbers honest: Mimir is a prefix-LM and should read the prompt with attention in both
directions; the community port we ran overnight reads left to right only. Through the group's own implementation with
the right attention Mimir scores 8.4 from memory against their 9.6, one standard error apart; the port gave 5.6.

## Corrections to what you told Olha
The story was right; four details were off. Closed book means memory only: in the base test the model does not "go
through tons of Wikipedia"; giving it Wikipedia is our addition, and nobody, including them, had published that. Their
tool paper is not about this benchmark: it trains a 3B model to call a Prolog interpreter on maths questions, so there
is no "54 percent with their tool" on DAISY and no tool number on DAISY at all, which is why the field's English results
are the comparison. The numbers are 8.4 from memory, 32.8 with the rule query, 60.6 with the oracle query that is a
ceiling, and 40 with a model that writes its own query. The 9.6 versus 8.4 sentence is exactly right.

## 5. Your three ways, corrected
Training memory is always the base layer, and it stops at the training cutoff. When a product has search, it does a
live search then writes: Google fires several related searches into its own index, ChatGPT sends reformulated queries to
Bing and its own crawler, Perplexity always searches, Claude decides per question whether the topic needs fresh
information. Cached answers served to everyone is not documented for any of them, and a measurement of Google's
overviews on 43,000 queries found the text changes about seven times in ten between visits with no link to how popular
the question is, so guess (a) is the one that does not hold. What does exist is caching of the prompt itself to save
computing, developer-side semantic caches, and Google's old answer boxes, which are copied passages, not generated text.

## 7 and 8. Scientific sources, for Olha
The search layer does try to prefer trustworthy pages, and Google gives extra weight to trust on health questions, but it
is not a science filter. Reddit and forums are among the most cited sources in AI answers, so anecdotes get in. Google's
overview once told people to put glue on pizza because of a forum joke, and in January 2026 it pulled some health answers
after a newspaper found errors. AI tools also invent references and cite retracted papers without saying so; in a 2025
test, four scholarly AI tools all cited retracted papers with no warning. Asking for peer-reviewed sources does help: it
changes what the model searches for and cites. It is not a guarantee. So ask for the DOI of every source, paste it into
doi.org, read the abstract yourself, and check the Retraction Watch database. For biology, start in PubMed, use tools
built on scholarly indexes (Consensus, Scite, Elicit), and treat a chatbot as a fast reader you must check.

## 6. AI engine optimisation
Real and partly measured. A 2024 study found pages with quotations, statistics and named sources got up to 40 percent
more space in AI answers, while keyword stuffing made things worse; citing sources helped a fifth-ranked page more than
double its visibility while the top page lost. In practice firms make sure a site is in Google's and Bing's indexes, get
it mentioned on Reddit and Wikipedia, and write pages that answer the sub-questions an AI would search for. Google says
this is just good SEO; the "llms.txt" file people sell is used by no engine. On politics two things are documented: a
Russian network of about 150 sites publishes millions of articles researchers say are written for AI crawlers, and tests
found chatbots repeating them (33 percent in one test, 5 percent in a stricter one); and a public US foreign-agent filing
shows Israel's foreign ministry paid a firm six million dollars to build websites to shape "GPT conversations". Whether
that changed any answer is unproven, one newspaper could not make three chatbots cite the sites, and nothing found ties
it specifically to 7 October. Poisoning research (PoisonedRAG and similar) shows the attack works in the lab.

## 9. Your claim about providers holding back
Mostly right on incentives, wrong on mechanism. Every search and every second of thinking costs the company money, so
free and cheap plans default to the quick path; OpenAI describes a router that sends a question to a fast model unless it
looks hard or you say "think hard about this"; deep research is capped to a few runs a month on cheaper plans. What is
not true is a secret deeper mode unlocked by "check academia". The model decides per question whether to search, based
on whether the answer could be stale, and your instructions change that decision; on the API the default effort is high
and there is no hidden per-question budget. "Check academia" changes which sources it looks at, which is exactly why it
works. Say how deep you want it, name the sources, and pick the research mode when it matters.

## My own questions from the conversation, answered
1. If Mimir saw a quarter of its 70 billion training tokens in Danish, why does it know so little of the Danish canon?
   Because a canon fact appears a handful of times in any corpus, and one-billion-parameter models do not retain
   rare facts; the literature calls this the long tail, and it does not improve with size until the model is very
   large. Their 70B comparison model gets 22.5 percent, Mimir 8.4, every other small model 1 to 6. Their own audit shows
   Mimir memorises almost no verbatim text, which is a feature for copyright and the same property that makes it forget
   who wrote De levendes Land. The right fix is the one we tested: keep the facts outside the model and fetch them.
2. What is the "engine" in "same engine, go faster"? Three candidates: parameters, tokens, seconds. Per parameter
   Mimir wins from memory. Per second it loses badly: its architecture runs several passes per token, so it is twenty
   times slower than Llama 1B on the same card through the port and still slower through the official path. A fair race
   reports both, which is why the page now carries exact match per second and per thousand tokens on one card.
3. Olha's picture, a man digging with bare hands: what exactly is the shovel? The shovel is retrieval, the fetched
   paragraphs. What our study adds to the picture is that the interesting question is not the shovel but whether the
   digger knows when to pick it up. The small models either never do or always do. None decides per hole.
4. Does the German idea of a controlled, non-leaking model fit what Denmark is building? Yes, that is the design: only
   consented data, open weights, runnable inside the building. The price is capability, 8.4 against 22.5. Our result is
   the argument for their approach: a controlled small model with a lookup beats the uncontrolled large model from
   memory, 33 to 40 against 22.5, on their own test. That is the sentence for the letter.
5. Why do Gemma and Qwen ask and the others never do? Two hurdles, format and decision. The 1B and 3B Llamas and Mimir
   never produce the search line at all; given a yes/no question first, Mimir and Llama 3B do decide, badly. Mimir's own
   chat template has a native tool-call format and a tenth of its training data is tool use, so the free-form line we
   offered may have been the wrong interface; the native-format test is next in the queue.
6. What would make the group adopt the tool rather than nod at it? A win on their own benchmark at matched cost,
   through their own implementation, with the decision to look up learned rather than scripted, and the same story
   repeated on a second Danish task where memory is worth something (their Multi Wiki QA, queued). Plus one fact they
   will want regardless: the community port of their model undercounts it by a third.
7. Your industrial-revolution analogy: does it hold? Partly. The loom needs the yarn fed right; the language model needs
   the sources fed right, which is why retrieval matters more than model size at this scale, and why people now
   optimise websites for the machine's eyes. The value moves to whoever controls what the machine reads.
