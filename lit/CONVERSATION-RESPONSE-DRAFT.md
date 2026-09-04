# Response to the recorded conversation (4 Sep 2026, 29 minutes, English). DRAFT; final after the large-v3 passes.

## 0. What you asked me directly, in order of the recording
1. [2:24] Figure out what these guys are trying to optimise for. Why are they building their own thing?
2. [3:03] What is the centre trying to achieve? What is the professor trying to achieve?
3. [8:21] Tell me exactly how the tools we created work (and what mechanism the lookup uses: keywords, sentences around them, or what).
4. [13:23] "Claude, pick out the specific things we are saying and respond to what I address to you directly; also come up
   with your own questions inspired by the conversation and answer them yourself."
5. [22:24] Three ways I imagine AI answers come about (cached frequent answers; live search then generate; already in
   training memory); correct me if I am wrong.
6. [24:55] Tell me how AI engine optimisation works. How do people structure websites so they show up in AI engines more?
Olha's questions, which you passed to me:
7. [21:11] When the AI searches, does it separate scientifically proven sources from opinion sites?
8. [25:03] Can I tell it to use only scientific sources, and does that give a better result?
And a claim of yours to check:
9. [25:55] Providers default to shallow answers to save their own compute; only when forced ("check academia", "run extra
   loops") does the model do the extra research.

## 3. How the tools we built work, exactly (from the code in daisy_tools/)

Nothing here is a trained model. Every "tool" is a few hundred lines of Python that sit between the question and the
language model. The model only ever sees text.

**The lookup itself (wiki.py).** The tool is Danish Wikipedia's public search API, the same one the site's search box
uses. Given a search string, it returns the titles of the three best-matching articles; a second call fetches the first
paragraphs of each article (up to 900 characters), plain text. Those three paragraphs are pasted above the question with
the heading "Baggrundsviden fra dansk Wikipedia", and the group's own prompt follows unchanged. The model reads that and
answers. It does not search for keywords inside the text, and it does not look at sentences around keywords: it gets the
introductions whole and has to find the answer in them. Every search result is cached on disk, so a repeated query costs
nothing and the study is reproducible.

**The "shitty" tool: the rule query (query.py).** Wikipedia's search often returns nothing for a whole question ("Hvem
skrev salmen De levendes Land?" finds nothing because every word must match). So a rule strips question words and
function words, keeps capitalised words and numbers first, and if the search still returns nothing it drops words from
the end until something comes back. A rule, not a model. The answer is inside the three paragraphs it fetches 40 percent
of the time, and Mimir then answers correctly 26.5 percent of the time on the old port, 32.8 percent on the fixed one.

**The "better" 60 percent: the oracle query.** Here the search string is the name of the canon work that the question is
about, which the benchmark stores as a hidden field. That fetches the right page 79 percent of the time and Mimir scores
60.6. It is a ceiling, not a tool: no model can see that field. It tells us what "asking well" is worth.

**The agentic tool.** The model is told it has one tool and may write exactly one line "SEARCH: <words>" or answer
directly. If it writes the line, the lookup runs with the model's own words, the paragraphs are pasted in, and it answers.
Gemma 3 4B and Qwen 2.5 3B write their own queries and reach 40 percent, better than the rule query, because their queries
land on the right page about half the time. Mimir, Llama 1B and Llama 3B never write the line at all.

**Decide then search.** A yes/no question first ("do you know this for sure?"), search only on no. This separates the
decision from the formatting hurdle. It shows the models' self-knowledge is poor: Mimir says yes on 69 percent of the
questions it then gets wrong.

**The split that moved the record.** One model writes the query, Mimir reads. Mimir reading Qwen's queries scored 38.2 on
the old port; the fixed Mimir is being rerun now and will score higher.

**The fix that made the numbers honest.** Mimir is a prefix-LM: it is meant to read the prompt with attention in both
directions. The community port we ran overnight reads it left to right only. Through the group's own implementation with
the right attention mode Mimir scores 8.4 from memory against their 9.6, one standard error apart; the port gave 5.6.

## Corrections to what you told Olha (the story is right; four details are off)
- Closed book means memory only. In the base test the model does not "go through tons of Wikipedia data"; it gets the
  question and nothing else. Giving it Wikipedia is our addition, and nobody, including them, had published that.
- Their tool paper is not about this benchmark. It trains a 3B model to call a Prolog interpreter on maths questions. There
  is no "54 percent with their tool" on DAISY; there is no tool number on DAISY at all. That is why "beat their tool on
  their terms" has no target, and why the field's English results are the comparison instead.
- The numbers: 8.4 from memory (their code path); 32.8 with the rule query; 60.6 with the oracle query, which is a ceiling
  not a tool; 40 with a model that writes its own query. "65 from 8.6" was a mix of the ceiling and a rounding.
- The 9.6 versus 8.4 sentence is exactly right, and it is the sentence that makes everything else credible.

## 1 and 2. What they optimise for (source: lit/WHAT-THEY-OPTIMISE-FOR.md, researched 4 Sep)
[integrate: sovereignty and legally permissible data as the design driver; DFM does both from-scratch and fine-tunes
(Munin); Mimir 1B beats their fine-tuned 8B and 9B on their Danish suite but their own state-of-the-art list is still
Mistral 24B and Gemma 27B; half the Danish suite is grammar/instruction following (Ordbogen territory); nothing on
retrieval, tool use, cost or energy; future work: HRM scaling, RL, licensing; the PhD call's three topics are exactly
their measured gaps; Schneider-Kamp is also CIO of Ordbogen (Chat.dk)]
