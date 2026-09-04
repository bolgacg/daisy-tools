# How AI answer engines work, and how people try to game them

Written 4 September 2026 for a recorded conversation between Bo (engineer, builds LLM tools) and his partner (biology master's applicant). Four questions, one section each. Every section ends with a plain-language answer of at most 150 words that can be read aloud, followed by a source list with URLs and arXiv ids.

Method note. Sources were fetched on 4 September 2026. A few primary pages (OpenAI's blog and help centre, NewsGuard, Snopes, MIT Technology Review, Perplexity's help centre) refuse automated fetches. Where that happened, the claim is taken from a second outlet that quotes the primary source, and the primary URL is still listed so it can be opened by hand. Anything not confirmed by at least one source is labelled unverified.

---

## 1. How does an AI answer actually get produced?

### 1.1 Scoring the three guesses

The three guesses were: (a) cached answers for frequent questions, (b) live search over relevant sources followed by generation, (c) the answer is already in the model's training memory. The honest scorecard is: (c) is always the base layer, (b) is what all the major products do when they search, and (a) is not documented for any of them and the best measurement available points against it for Google.

Guess (c), training memory. A language model stores what it learned during training in its weights. The 2020 paper that named retrieval-augmented generation (RAG) calls this "parametric memory" and contrasts it with "non-parametric memory", meaning documents fetched at answer time. Lewis and colleagues showed that combining the two produces "more specific, diverse and factual language than a state-of-the-art parametric-only seq2seq baseline" (Lewis et al. 2020, arXiv 2005.11401, NeurIPS 2020). Every chatbot answer starts from parametric memory. Without a search tool, that is all there is, and the model's picture of the world stops at its training cutoff.

Guess (b), search then generate. This is RAG applied to the live web. All four systems below do it: a query (or several) goes to a search index, pages come back, the model reads them and writes an answer with citations. The differences are in whose index is used, whether every answer triggers a search, and how many searches are run.

Guess (a), cached answers. Three things get confused here:

- Prompt caching. Providers cache the computation for a repeated prompt prefix, not the answer. Anthropic's documentation: "Prompt caching optimizes your API usage by allowing resuming from specific prefixes in your prompts." The cache lives five minutes by default and cache reads cost one tenth of normal input tokens. This is a developer feature and it does not return a stored answer to a different user.
- Semantic caches. Open-source tools such as GPTCache ("a project dedicated to building a semantic cache for storing LLM responses") let a developer return a stored answer when a new question is similar enough to an old one. Companies building on top of the APIs may use this. None of Google, OpenAI, Anthropic or Perplexity documents doing it for their consumer chat products.
- Featured snippets. Google's classic answer box is a pre-extracted passage from one indexed page, not a generated text: "Google systems determine whether a page would make a good featured snippet for a user's search request, and if so, elevates it." Site owners cannot mark a page for it.

For AI Overviews specifically, Ahrefs measured this in November 2025 on more than 43,000 keywords, each observed at least 16 times. The AI Overview text changed about 70 percent of the time between consecutive observations, persisted on average 2.15 days, and 45.5 percent of cited URLs changed per refresh. The correlation between search volume and change rate was minus 0.014, which is the opposite of what caching popular queries would produce. The meaning stayed stable (cosine similarity 0.95) because the underlying sources are stable. Refreshing the page gives a differently worded overview with partly different citations. So the answer is regenerated, from a mostly fixed set of sources, and the "cached popular answers" theory is not supported.

Google's cost reduction is also not caching. On the first quarter 2024 earnings call Sundar Pichai said machine costs for generative answers had fallen 80 percent since the Labs launch, "driven by hardware, engineering, and technical breakthroughs".

### 1.2 Google AI Overviews and AI Mode

Launched in the United States on 14 May 2024 and extended to more than 100 countries in October 2024. Google's launch post describes "a new Gemini model customized for Google Search" that brings "multi-step reasoning, planning and multimodality" together with its search systems. Google Search Central states that its "generative AI features on Google Search are rooted in our core Search ranking and quality systems", that there are "no additional requirements to appear in AI Overviews or AI Mode", and that a page only needs to be indexed and eligible to show a snippet.

Both features "may use a 'query fan-out' technique" that issues "multiple related searches across subtopics and data sources". For AI Mode, Google's I/O 2025 post says: "AI Mode uses our query fan-out technique, breaking down your question into subtopics and issuing a multitude of queries simultaneously on your behalf." Its Deep Search mode "can issue hundreds of searches, reason across disparate pieces of information, and create an expert-level fully-cited report."

AI Overviews appear "when our systems determine that generative AI can be especially helpful". Google's own help page adds: "AI Overviews can and will make mistakes." After the May 2024 incidents (section 2), Google's head of Search, Liz Reid, wrote that AI Overviews do not make things up "in the ways that other LLM products might", because the model is wired into the ranking systems and is built to show text that is backed by top-ranked web results rather than to free-write from training data.

So Google's product is a search engine first: the fan-out queries hit Google's own index, ranking decides what the model gets to read, and the links come from those ranked results.

### 1.3 ChatGPT with search

Launched 31 October 2024. OpenAI's help centre says ChatGPT "may search the web automatically when your question would benefit from current information, or you can manually choose search". When it searches, it "can turn the request into one or more search queries, retrieve relevant results, and use those results to generate an answer with links to sources". It "may initially query a search partner using a reformulated search query, and after reviewing initial results, ChatGPT search may send additional, more specific queries to other search providers".

Whose index? OpenAI's enterprise documentation states ChatGPT "may share disassociated search queries with the Bing search engine to return web results", and that it also uses "content provided directly by our partners" (publisher and platform licensing deals, including Reddit from May 2024). OpenAI also runs its own crawler, OAI-SearchBot, to index pages for ChatGPT search. So ChatGPT is a chat model that calls Microsoft's index plus its own crawl plus licensed feeds, and the model decides per question whether to search.

### 1.4 Perplexity

Perplexity is an answer engine: essentially every question triggers a web search, and the answer is written from the retrieved pages with numbered citations. It runs its own crawler. Its developer docs state: "PerplexityBot is designed to surface and link websites in search results on Perplexity. It is not used to crawl content for AI foundation models." A second agent, Perplexity-User, fetches a page at question time: "When users ask Perplexity a question, it might visit a web page to help provide an accurate answer and include a link to the page in its response."

### 1.5 Claude with web search

Anthropic's API documentation is the most explicit about the decision policy. "Claude determines when to search based on the prompt." The API runs the searches and returns results, and "this process can repeat multiple times throughout a single request." Claude searches "when the request depends on information that is current, changing, or outside its training data": recent events, current prices or statistics, facts about organisations or people that may have changed, and "explicit requests to search or look something up". It answers without searching for "established facts, math, science fundamentals, or coding concepts", creative writing, or analysis of text already in the conversation. "Triggering is steerable through your system prompt: you can encourage Claude to search more readily or to prefer answering directly." Simple factual queries typically use one to three searches; comparative research can use ten or more. Developers can cap searches with `max_uses`, restrict results with `allowed_domains` or `blocked_domains`, and pay 10 dollars per 1,000 searches on top of tokens. Citations are always on.

In the consumer app, Anthropic's help centre says: "When you ask about topics that benefit from current information, Claude invokes a search tool to inform and ground its generated responses." The Research feature (April 2025) goes further: Claude "operates agentively, conducting multiple searches that build on each other while determining exactly what to investigate next."

### 1.6 Chat model with a web tool versus a search engine's AI mode

- Who owns the index. Google and Perplexity search their own indexes. ChatGPT searches Bing plus its own crawl plus partner feeds. Claude calls a third-party search API.
- Whether every answer searches. Perplexity: yes by design. Google AI Mode: yes. AI Overviews: only when Google's systems decide to show one. ChatGPT and Claude: the model decides per question, unless you force it.
- Where ranking comes from. In Google's product the ranking systems and their quality signals (section 2) decide what the model reads. In a chat model, the search provider ranks, then the model picks which hits to open and cite, and a system prompt or user instruction can shift that choice.
- What the answer is anchored to. Google says its overview must be backed by top results. A chat model blends retrieved text with training memory and can still answer from memory alone.

### Plain-language answer (read aloud)

Every AI answer starts from what the model memorised during training. That is the base layer and it stops at the training cutoff. When the product has search, it does a live web search first: Google fires off several related searches into its own index, ChatGPT sends queries to Bing and its own crawler, Perplexity always searches, and Claude decides per question whether the topic needs fresh information. The model then reads the pages it got back and writes the answer with citations. Stored answers being served to everyone is not something any of them documents, and a measurement of Google's overviews found the text changes about seven times out of ten between visits, with no link to how popular the question is. What does exist is caching of the prompt itself to save computing, and Google's old answer boxes, which are copied passages rather than generated text.

### Sources for section 1

- Lewis et al. 2020, "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", NeurIPS 2020, arXiv 2005.11401: https://arxiv.org/abs/2005.11401
- Google Search Central, "AI features and your website": https://developers.google.com/search/docs/appearance/ai-features
- Google Search Central, "Google's Guide to Optimizing for Generative AI Features": https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- Google, "Generative AI in Search: Let Google do the searching for you", 14 May 2024: https://blog.google/products/search/generative-ai-google-search-may-2024/
- Google, "AI Mode in Google Search: Updates from Google I/O 2025", 20 May 2025: https://blog.google/products-and-platforms/products/search/google-search-ai-mode-update/
- Google help, "AI Overviews and AI Mode in Search": https://support.google.com/websearch/answer/14901683
- Google, Liz Reid, "AI Overviews: About last week", 30 May 2024: https://blog.google/products/search/ai-overviews-update-may-2024/ (quoted via Search Engine Land: https://searchengineland.com/google-explains-how-it-is-improving-its-ai-overviews-442800)
- Google Search Central, "Featured snippets and your website": https://developers.google.com/search/docs/appearance/featured-snippets
- Ahrefs, "AI Overviews Change Every 2 Days (But Never Change Their Mind)", 11 November 2025: https://ahrefs.com/blog/ai-overview-change/
- Search Engine Roundtable on the Q1 2024 earnings call (80 percent cost reduction): https://www.seroundtable.com/google-sge-ai-answers-cost-80-less-37326.html
- OpenAI, "Introducing ChatGPT search", 31 October 2024: https://openai.com/index/introducing-chatgpt-search/
- OpenAI help, "Searching the web with ChatGPT": https://help.openai.com/en/articles/9237897-chatgpt-search
- OpenAI help, "ChatGPT search for Enterprise and Edu" (Bing statement): https://help.openai.com/en/articles/10093903-chatgpt-search-for-enterprise-and-edu
- OpenAI crawlers (OAI-SearchBot): https://platform.openai.com/docs/bots
- OpenAI and Reddit partnership, May 2024: https://openai.com/index/openai-and-reddit-partnership/
- Perplexity crawler documentation: https://docs.perplexity.ai/guides/bots
- Perplexity help, "How does Perplexity work?": https://www.perplexity.ai/help-center/en/articles/10352895-how-does-perplexity-work
- Anthropic, web search tool documentation: https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool
- Anthropic, prompt caching documentation: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- Anthropic help, "Enable and use web search": https://support.claude.com/en/articles/10684626-enable-and-use-web-search
- Anthropic, "Claude takes research to new places", 15 April 2025: https://claude.com/blog/research
- GPTCache (semantic cache, open source): https://github.com/zilliztech/GPTCache

---

## 2. Does it tell science from opinion, and can I ask for scientific sources only?

### 2.1 What the ranking layer does and does not filter

Google's ranking systems try to reward what Google calls E-E-A-T: experience, expertise, authoritativeness and trustworthiness. Its documentation says "trust is most important" and that for health, money and safety topics "our systems give even more weight to content that aligns with strong E-E-A-T for topics that could significantly impact the health, financial stability, or safety of people, or the welfare or well-being of society. We call these 'Your Money or Your Life' topics, or YMYL for short." The Search Quality Rater Guidelines (latest edition 11 September 2025) describe how human raters judge this, but "Search raters have no control over how pages rank. Rater data is not used directly in our ranking algorithms."

That is a quality preference, not a scientific filter. Ranking also rewards relevance, freshness and popularity, and AI products lean heavily on community sites. Semrush analysed about 100 million citations over 230,000 prompts between July and October 2025: in early August Reddit appeared in roughly 60 percent of ChatGPT answers and Wikipedia in about 55 percent, before both dropped sharply in September. A Peec AI study of 30 million cited sources found Reddit the most-cited domain across ChatGPT, Google AI Mode, Gemini, Perplexity and AI Overviews. Google pays Reddit about 60 million dollars a year for data (reported February 2024) and OpenAI signed its own Reddit deal in May 2024. So yes, "Aunt Clara's life experience" on a forum can and does end up in AI answers. Google admitted as much when, after May 2024, it updated its systems "to limit the use of user-generated content in responses that could offer misleading advice".

### 2.2 Known failures

The glue and rocks incidents. In the first weeks after launch, AI Overviews told users to add glue to pizza sauce (traced by reporters to an old joke comment on a Reddit thread) and to eat a small rock a day (satire from The Onion, republished on a geology software company's site). Google's explanation, from Liz Reid's 30 May 2024 post: "data voids" where almost nobody had asked the question before, satire the system did not recognise, and forum content read as advice. Google then built detection for nonsensical queries, limited satire and user-generated content in answers, added triggering restrictions where overviews were not helpful, and "for health topics, launched additional triggering refinements to enhance quality protections".

Health again, January 2026. A Guardian investigation found AI Overviews giving lab reference ranges without context (for example "normal range for liver function tests"), listing a Pap test as a vaginal cancer exam, and advising pancreatic cancer patients to avoid high-fat foods, which specialists said was wrong. Google removed AI Overviews for some of these queries and said it works to "make broad improvements" rather than comment on individual removals.

Citation failures. The Tow Center at Columbia tested eight AI search tools with 1,600 queries in March 2025. More than 60 percent of answers were wrong; Perplexity was wrong 37 percent of the time and Grok 3 94 percent. Tools "fabricated links and cited syndicated and copied versions of articles", and paid versions gave more confidently wrong answers than free ones. Earlier, Walters and Wilder (Scientific Reports, 2023) asked ChatGPT for literature reviews on 42 topics: 55 percent of GPT-3.5's citations and 18 percent of GPT-4's were fabricated, and of the real ones 43 percent (GPT-3.5) and 24 percent (GPT-4) contained substantive errors.

Retracted papers. Thelwall and Katsirea (Learned Publishing, 2025) asked ChatGPT to assess 217 retracted or otherwise concerning papers, 30 times each. None of the 6,510 reports mentioned the retraction, and 190 papers were rated world-leading or internationally excellent. Gu and colleagues (Journal of Advanced Research, 2025) tested GPT-4o on 21 retracted cancer-imaging papers: five answers used retracted work, only three of those warned about it. MIT Technology Review (September 2025) ran a similar test on research-specific tools: of 21 retracted papers, Elicit referenced five, Ai2 ScholarQA 17, Perplexity 11 and Consensus 18, all without flagging the retraction.

### 2.3 Tools built for scientific sources

- Google Scholar (scholar.google.com): Google's index of scholarly literature. Free, broad, includes preprints and some low-quality venues.
- PubMed (pubmed.ncbi.nlm.nih.gov): the US National Library of Medicine's index of biomedical literature. Curated, the right first stop for biology and medicine.
- Semantic Scholar (semanticscholar.org, Allen Institute for AI) and OpenAlex (openalex.org): open indexes of 200 million plus papers with citation graphs; the data layer under several of the tools below.
- Consensus (consensus.app): searches "over 200 million scientific documents" aggregated from Semantic Scholar, OpenAlex, its own crawl and publisher partnerships; re-ranks the top 1,500 hits by "recency of publication, citation count, journal reputation and impact"; shows a Consensus Meter for yes/no questions. Its own documentation admits it may "misinterpret a paper and summarize it incorrectly".
- Elicit (elicit.com): finds papers and extracts data from them; states it extracts "directly from papers" and highlights the source passage. An independent 2025 comparison in Cochrane Evidence Synthesis and Methods (Lau and Golder) found Elicit's sensitivity "poor, averaging 39.5%" against 94.5 percent for conventional systematic searches, with higher precision. Good for a first pass, not a substitute for a proper search.
- Scite (scite.ai): "Smart Citations show how later research has supported, challenged, or discussed a paper", built from 1.6 billion citation statements. Useful for checking whether a claim was later contradicted.
- Retraction Watch Database (retractiondatabase.org): acquired by Crossref on 12 September 2023 and made public; about 50,000 retraction records at that time. Check any key paper here.
- Perplexity: its app has an academic source setting (described by third-party guides; Perplexity's own help page could not be fetched). Its developer docs implement the same idea with a domain filter: restricting to arxiv.org, pubmed.ncbi.nlm.nih.gov, nature.com, science.org, .edu and similar "restrict[s] results to peer-reviewed journals, preprint servers, and academic databases".
- OpenAI deep research (from February 2025): multi-step browsing that runs for minutes and returns a cited report. Limits as of April 2025: Free 5 lightweight tasks a month; Plus and Team 10 full plus 15 lightweight; Pro 125 plus 125.
- Claude Research (from April 2025) in the app, and in the API the `allowed_domains` parameter, which is a hard filter: Claude can only see results from the listed domains.
- Google AI Mode Deep Search: "hundreds of searches" with a cited report.

### 2.4 Can you ask for scientific sources only, and does it help?

Yes, and it helps, with two limits.

What an instruction changes. In a chat app, "use only peer-reviewed sources" changes the search queries the model writes (OpenAI: the model turns the request "into one or more search queries") and which hits it chooses to read and cite. Anthropic states directly that search triggering "is steerable through your system prompt". So the pool of sources shifts toward journals and university sites.

What it does not do. It is not a hard filter in the consumer apps. Search still ranks by relevance, so a blog post that explains a paper well can outrank the paper. If the model finds nothing it may fall back to memory and produce a plausible but fabricated reference (the Walters and Wilder rates above). And none of the tools tested by MIT Technology Review checked retraction status. Hard filters exist only where you control the tool: Claude's `allowed_domains`, Perplexity's domain filter, or tools such as Consensus and Scite that only index scholarly work in the first place.

### 2.5 Practical advice for a biology student

How to phrase it. Something like: "Answer using only peer-reviewed papers or university and government science pages. For every claim give the paper's title, first author, year, journal and DOI. If you cannot find a peer-reviewed source, say so instead of guessing. Say whether each source is a preprint or peer-reviewed, and whether it has been retracted." Asking for the DOI is the single most useful line, because a fabricated citation usually fails at the DOI.

Which tool for which job.

- To find the literature: PubMed and Google Scholar first, Semantic Scholar for citation chasing.
- To get a fast synthesis with sources: Consensus or Elicit, then open the papers.
- To check whether a finding held up: Scite.
- For a broad overview that needs the general web too: ChatGPT deep research or Claude Research, with the instruction above, and then verify.

How to verify.

- Paste the DOI into doi.org. If it does not resolve, the reference is fake.
- Read the abstract yourself. Check that the paper says what the AI says it says. Consensus's own docs admit misreadings happen.
- Check the paper in the Retraction Watch Database.
- Note preprint versus peer-reviewed (bioRxiv, medRxiv and arXiv are preprint servers; the paper may never have been reviewed).
- Check the journal and the date. A 2011 result may have been overturned.
- For anything about health or safety, prefer reviews and guidelines over single studies.

The limit. Even with perfect sources, the model can misread a paper. Tow's finding that paid tools give more confident wrong answers applies here too. The AI is a fast reader that must be checked, not an authority.

### Plain-language answer (read aloud)

The search layer does try to prefer trustworthy pages, and Google gives extra weight to trust on health questions. But it is not a science filter. Reddit and other forums are among the most cited sources, so anecdotes do get in. Google's overview once told people to put glue on pizza because of a forum joke, and in January 2026 it pulled some health answers after a newspaper found errors. AI tools also invent references and cite retracted papers without saying so. Asking for peer-reviewed sources does help: it changes what the AI searches for and cites. It is not a guarantee. So ask for the DOI of every source, paste it into doi.org, read the abstract, and check the Retraction Watch database. For biology, start in PubMed, use tools built on scholarly indexes like Consensus or Scite, and treat a chatbot as a fast reader you must check.

### Sources for section 2

- Google Search Central, "Creating helpful, reliable, people-first content" (E-E-A-T, YMYL, raters): https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- Google Search Quality Rater Guidelines, 11 September 2025 edition: https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf
- Semrush, "The Most-Cited Domains in AI: A 3-Month Study", 10 November 2025: https://www.semrush.com/blog/most-cited-domains-ai/
- Search Engine Land on the Peec AI study of 30 million sources: https://searchengineland.com/ai-search-engines-cite-reddit-youtube-and-linkedin-most-study-473138
- CBS News on the Google and Reddit deal, February 2024: https://www.cbsnews.com/news/google-reddit-60-million-deal-ai-training/
- Columbia Journalism Review, "Reddit Is Winning the AI Game" (OpenAI deal): https://www.cjr.org/analysis/reddit-winning-ai-licensing-deals-openai-google-gemini-answers-rsl.php
- Google, "AI Overviews: About last week", 30 May 2024: https://blog.google/products/search/ai-overviews-update-may-2024/
- The Verge on the glue and rocks answers, 23 May 2024: https://www.theverge.com/2024/5/23/24162896/google-ai-overview-hallucinations-glue-in-pizza
- Euronews on the January 2026 health rollback: https://www.euronews.com/next/2026/01/12/google-removes-some-health-related-questions-from-its-ai-overviews-following-accuracy-conc
- TechCrunch, 11 January 2026: https://techcrunch.com/2026/01/11/google-removes-ai-overviews-for-certain-medical-queries
- Tow Center, "AI Search Has a Citation Problem", 6 March 2025: https://www.cjr.org/tow_center/we-compared-eight-ai-search-engines-theyre-all-bad-at-citing-news.php
- Walters and Wilder 2023, Scientific Reports 13:14045: https://www.nature.com/articles/s41598-023-41032-5
- Thelwall and Katsirea 2025, Learned Publishing, doi 10.1002/leap.2018: https://onlinelibrary.wiley.com/doi/10.1002/leap.2018 (summary: https://techxplore.com/news/2025-08-chatgpt-article-retractions-errors-literature.html)
- Gu et al. 2025, Journal of Advanced Research (retracted cancer imaging papers): https://pmc.ncbi.nlm.nih.gov/articles/PMC12126723/
- MIT Technology Review, "AI models are using material from retracted scientific papers", 23 September 2025: https://www.technologyreview.com/2025/09/23/1123897/ai-models-are-using-material-from-retracted-scientific-papers/
- Consensus, "How Consensus works": https://consensus.app/home/blog/how-consensus-works/
- Elicit, reliability statement: https://support.elicit.com/en/articles/552897
- Lau and Golder 2025, Cochrane Evidence Synthesis and Methods (Elicit versus traditional searching): https://pmc.ncbi.nlm.nih.gov/articles/PMC12483133/
- Scite: https://scite.ai/
- Crossref and Retraction Watch, 12 September 2023: https://www.crossref.org/blog/news-crossref-and-retraction-watch/
- Retraction Watch Database: https://retractiondatabase.org/
- Perplexity developer docs, academic search with domain filters: https://docs.perplexity.ai/docs/cookbook/articles/academic-search/README
- OpenAI, "Introducing deep research", 2 February 2025: https://openai.com/index/introducing-deep-research/ ; limits per plan as reported by The Decoder, 25 April 2025: https://the-decoder.com/deep-research-feature-now-available-to-free-chatgpt-users/
- Anthropic web search tool (`allowed_domains`): https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool
- PubMed: https://pubmed.ncbi.nlm.nih.gov/ ; Google Scholar: https://scholar.google.com/ ; Semantic Scholar: https://www.semanticscholar.org/ ; OpenAlex: https://openalex.org/ ; DOI resolver: https://doi.org/

---

## 3. How does AI engine optimisation work, and is it used for political narratives?

### 3.1 What the research says

The term Generative Engine Optimization comes from Aggarwal and colleagues (Princeton, Georgia Tech, Allen Institute, IIT Delhi), presented at KDD 2024 (arXiv 2311.09735). They built a benchmark of diverse queries with associated web sources, rewrote the source pages in nine ways, and measured how much of the generated answer each source occupied (position-adjusted word count) and how prominent it seemed (subjective impression). The abstract claims GEO "can boost visibility by up to 40% in generative engine responses".

Reported gains versus unmodified pages (position-adjusted word count, then subjective impression):

- Quotation addition: plus 41 percent, plus 28 percent
- Statistics addition: plus 33 percent, plus 21 percent
- Cite sources: plus 28 percent, plus 13 percent
- Fluency optimisation: plus 29 percent, plus 12 percent
- Technical terms: plus 18 percent
- Easy to understand: plus 14 percent
- Authoritative tone: plus 12 percent
- Unique words: plus 6 percent
- Keyword stuffing: minus 9 percent

Two caveats. The paper says gains "vary across domains", and adding citations helped lower-ranked pages far more than top ones: the cite-sources edit raised visibility of the fifth-ranked page by 115 percent while the top page lost 30 percent on average. The experiments ran on the authors' own generative engine and on Perplexity; results on Google's or OpenAI's current systems are not measured in the paper.

The practical reading: pages that quote named sources, carry numbers, and read fluently get picked up more; repeating keywords does nothing or hurts.

### 3.2 What practitioners do, and what the platforms say

- Be in the indexes that feed the engines. Google's index for AI Overviews and AI Mode, Bing for ChatGPT, Perplexity's own crawl. Blocking OAI-SearchBot or PerplexityBot removes you from those answers.
- Get cited by the sources the engines already trust. Wikipedia, Reddit, YouTube and LinkedIn dominate the citation tables (section 2.1). Agencies seed Reddit threads and Wikipedia references for this reason.
- Structured content. Clear headings, direct answers to likely fan-out sub-questions, statistics and quotations, as in 3.1.
- llms.txt. A proposal by Jeremy Howard (3 September 2024) for a Markdown index of a site for language models. Google's John Mueller said in April 2025 that no AI service has said it uses the file and compared it to the long-ignored keywords meta tag; Google's own guide tells site owners to ignore such hacks.
- Google's official position (guide last updated 10 July 2026): "optimizing for generative AI search is optimizing for the search experience, and thus still SEO", and "structured data isn't required for generative AI search, and there's no special schema.org markup you need to add."

### 3.3 Documented manipulation of AI answers through web content

State-linked. The Pravda network (also called Portal Kombat), first documented by France's VIGINUM agency in February 2024, is a set of about 150 pro-Kremlin websites across 49 countries that republish content in dozens of languages. The American Sunlight Project (report of 26 February 2025) found the sites are nearly unusable for humans ("no search function, a generic navigation menu, and dysfunctional scrolling") yet publish at least 3.6 million articles a year, and concluded the network "isn't targeting humans, but an automated audience: web crawlers". They named the tactic "LLM grooming". NewsGuard (6 March 2025) then tested ten chatbots (ChatGPT, Copilot, Gemini, Claude, Perplexity, Grok, Meta AI, Mistral's Le Chat, Pi, You.com) on a set of false narratives and reported that they "repeated falsehoods from the Pravda network more than 33 percent of the time". DFRLab (8 April 2026) found roughly 40,000 English-language Pravda pages in Common Crawl, the public web archive used in most open training pipelines, by November 2025, up from 37 a year earlier, and reproduced an RT article nearly verbatim from an open base model.

Caveat on the 33 percent. An Al Jazeera opinion piece (8 July 2025) noted NewsGuard did not release its prompts, that two thirds of the prompts were written to provoke a falsehood, and that cautious responses were counted as failures; the authors' own audit found about 5 percent and suggested a "data void" explanation, where chatbots quote dubious sites because nothing better exists on the topic. Both readings agree the content reaches the models; they disagree on how often it changes an answer.

Peer-reviewed attacks. PoisonedRAG (Zou, Geng, Wang, Jia; USENIX Security 2025; arXiv 2402.07867) showed that injecting a handful of crafted texts into a RAG system's document store makes it return an attacker-chosen answer to a chosen question. Nestaas, Debenedetti and Tramèr (ETH Zurich, arXiv 2406.18382) demonstrated "preference manipulation attacks", where text on a website or in plugin documentation makes an LLM promote the attacker's product and disparage competitors, tested on Bing, Perplexity and GPT-4 and Claude plugin APIs. Pfrommer and colleagues (arXiv 2406.03589) showed prompt injections hidden in product pages re-rank the sources a conversational search engine cites, and that the attack transfers to Perplexity.

### 3.4 Political GEO firms: documented versus unverified

Documented. A filing under the US Foreign Agents Registration Act, first reported by Responsible Statecraft on 29 September 2025, shows Israel's Ministry of Foreign Affairs contracted Clock Tower X LLC, a firm led by Brad Parscale, for 6 million dollars (the Washington Examiner later reported a further 3 million dollar advertising budget and a signing date of August 2025). The contract, whose stated purpose is a US campaign "to combat antisemitism", says the money must fund the "deployment of websites and content to deliver [generative pre-trained transformer] framing results on GPT conversations" and "monthly search engine optimization campaigns", with at least 80 percent of content aimed at Generation Z and a target of 50 million impressions a month. Ynet reports this sits inside Project 545, a 545 million shekel (about 145 million dollar) public diplomacy budget for 2025. This is, as far as this research found, the only public document in which a government contract explicitly names shaping GPT conversations as a deliverable.

What is not documented. That it worked. The Washington Examiner (25 March 2026) reported it "wasn't able to get ChatGPT, Google Gemini, or Claude to cite websites from Clock Tower X's network through prompts". Parscale said the activity was "explicitly disclosed in our FARA filings"; OpenAI did not respond. The viral claim that "Israel signed a deal with ChatGPT" is false: Snopes (22 December 2025) confirmed the contract is with a PR firm, not OpenAI.

Related but different. In May 2024 OpenAI reported disrupting STOIC, a Tel Aviv political marketing firm that used OpenAI models to write pro-Israel articles and comments about Gaza posted through fake accounts on Facebook, Instagram, X, YouTube and Telegram. That is AI-generated social media content, not optimisation of AI answers, and OpenAI and Meta said it drew "little, if any, authentic engagement".

Unverified. No source found in this research documents a campaign aimed specifically at how AI answers describe 7 October 2023. The Clock Tower X filing speaks of antisemitism and pro-Israel framing in general. Claims naming specific firms, budgets or results beyond the filing above (for example a 46.5 million dollar figure circulating in some outlets) could not be verified and should be treated as unconfirmed. Commercial GEO agencies exist openly and sell exactly the techniques in 3.1 and 3.2; whether any given one takes political clients is not something the public record shows except through filings like the one above.

### Plain-language answer (read aloud)

AI engine optimisation is real and partly measured. A 2024 study found that pages with quotations, statistics and named sources got up to 40 percent more space in AI answers, while keyword stuffing made things worse. In practice, firms make sure a site is in Google's and Bing's indexes, get it mentioned on Reddit and Wikipedia, and write pages that answer the sub-questions an AI would search for. On politics, two things are documented. A Russian network of about 150 sites publishes millions of articles a year that researchers say are meant for AI crawlers rather than readers, and tests found chatbots repeating them. And a public US filing shows Israel's foreign ministry paid a firm to build websites to shape "GPT conversations". Whether that Israeli campaign changed any answer is unproven, one newspaper could not make chatbots cite the sites, and nothing found ties it specifically to 7 October.

### Sources for section 3

- Aggarwal et al. 2024, "GEO: Generative Engine Optimization", KDD 2024, arXiv 2311.09735: https://arxiv.org/abs/2311.09735
- Google Search Central, AI optimisation guide (no special GEO needed): https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- llms.txt proposal: https://llmstxt.org/
- Search Engine Journal, "Google Says LLMs.Txt Comparable To Keywords Meta Tag", April 2025: https://www.searchenginejournal.com/google-says-llms-txt-comparable-to-keywords-meta-tag/544804/
- Search Engine Roundtable, "Google Search Team Does Not Endorse LLMs.txt Files": https://www.seroundtable.com/google-does-not-endorse-llms-txt-40789.html
- Semrush most-cited domains study: https://www.semrush.com/blog/most-cited-domains-ai/
- OpenAI enterprise search help (Bing): https://help.openai.com/en/articles/10093903-chatgpt-search-for-enterprise-and-edu
- NewsGuard, "A Well-funded Moscow-based Global 'News' Network has Infected Western Artificial Intelligence Tools", 6 March 2025: https://www.newsguardtech.com/special-reports/moscow-based-global-news-network-infected-western-artificial-intelligence-russian-propaganda/ (figures confirmed via France 24, 10 March 2025: https://www.france24.com/en/live-news/20250310-russian-disinformation-infects-ai-chatbots-researchers-warn)
- American Sunlight Project, Pravda network report, 26 February 2025, via Bulletin of the Atomic Scientists, March 2025: https://thebulletin.org/2025/03/russian-networks-flood-the-internet-with-propaganda-aiming-to-corrupt-ai-chatbots/
- Wikipedia, "Pravda network" (VIGINUM, February 2024): https://en.wikipedia.org/wiki/Pravda_network
- DFRLab, "Pravda in the pipeline", 8 April 2026: https://dfrlab.org/2026/04/08/pravda-in-the-pipeline/
- Al Jazeera opinion, "Is Russia really 'grooming' Western AI?", 8 July 2025: https://www.aljazeera.com/opinions/2025/7/8/is-russia-really-grooming-western
- Zou et al., "PoisonedRAG", USENIX Security 2025, arXiv 2402.07867: https://www.usenix.org/conference/usenixsecurity25/presentation/zou-poisonedrag
- Nestaas, Debenedetti, Tramèr 2024, "Adversarial Search Engine Optimization for Large Language Models", arXiv 2406.18382: https://arxiv.org/abs/2406.18382
- Pfrommer et al. 2024, "Ranking Manipulation for Conversational Search Engines", arXiv 2406.03589: https://arxiv.org/abs/2406.03589
- Responsible Statecraft, "Israel wants to train ChatGPT to be more pro-Israel", 29 September 2025: https://responsiblestatecraft.org/israel-chatgpt/
- Washington Examiner, "Israel funds front websites in attempt to manipulate ChatGPT", 25 March 2026: https://www.washingtonexaminer.com/news/investigations/4501168/israel-funds-front-websites-push-chatgpt-promote-pro-war-messaging/
- Snopes, "Israel didn't sign a deal with ChatGPT", 22 December 2025: https://www.snopes.com/news/2025/12/22/israel-contract-chatgpt/
- Ynet on Project 545: https://www.ynetnews.com/tech-and-digital/article/rj00kxqzaxx
- OpenAI, "Disrupting deceptive uses of AI by covert influence operations", 30 May 2024: https://openai.com/index/disrupting-deceptive-uses-of-ai-by-covert-influence-operations/ ; NBC News coverage: https://www.nbcnews.com/tech/security/meta-openai-say-disrupted-israeli-companys-influence-campaign-rcna154774

---

## 4. Bo's claim: providers default to shallow answers to save compute, and only dig deeper when forced

### 4.1 What is true

Defaults are real and they are set on the cheap side. OpenAI's reasoning models expose a `reasoning_effort` setting that "tells the model how much to think before it answers", with values from none through minimal, low, medium, high, xhigh to max, and "defaults vary by model"; the first GPT-5 defaulted to medium and, per Microsoft's Azure documentation, GPT-5.1 defaults to none. A separate `verbosity` setting (low, medium, high) controls length, default medium. Google's Gemini uses "dynamic thinking by default, automatically adjusting the amount of reasoning effort based on the complexity of the request", and bills "the sum of output tokens and thinking tokens". OpenAI's Model Spec (18 August 2026 edition) instructs the model to "be thorough but efficient, while respecting length limits".

The consumer router picks the cheaper path unless told otherwise. OpenAI's GPT-5 launch describes "a real-time router that quickly decides which to use based on conversation type, complexity, tool needs, and your explicit intent (for example, if you say 'think hard about this' in the prompt)". That is exactly Bo's mechanism, stated by the vendor: a fast model by default, a reasoning model when the question looks hard or the user asks.

Effort settings reduce research, not just words. Anthropic's documentation says that at lower effort "Claude still thinks on sufficiently difficult problems, but thinks less", and that "lower effort also means fewer and terser tool calls", including fewer searches. For one model version the docs say that at low effort "the model scopes its work to what was asked rather than doing more than requested".

Cost is the reason. Google cut its per-answer machine cost by 80 percent and said so to investors. Anthropic charges 10 dollars per 1,000 searches plus tokens for everything retrieved. Every extra search and every thinking token costs the provider money on a subscription and costs the developer money on the API.

Tiers ration the deep modes. Deep research is capped per month (5 lightweight tasks free; 10 full plus 15 lightweight on Plus; 125 plus 125 on Pro, as of April 2025). ChatGPT's manually selected Thinking mode has a separate weekly cap on paid plans. Claude's plans meter a five-hour session window and a weekly cap, and the help centre says consumption depends on "tool use such as Research". So a free or cheap tier does get the shallow path most of the time.

### 4.2 What is not accurate

"Shallow by default" is a product choice, not a model property. On Anthropic's API the default is high effort: "By default, Claude uses high effort, spending as many tokens as needed for excellent results." The developer sets the ceiling with `max_tokens`. There is no hidden per-question token budget on the API; there is a bill.

The model decides per query whether to research. Anthropic's list of when Claude searches (current, changing, or unknown information; explicit requests) and when it does not (stable facts, creative writing, analysis of provided text) is a policy applied to each question, not a global setting to do the minimum. OpenAI's help centre says the same: ChatGPT "may search the web automatically when your question would benefit from current information". Simple questions get one to three searches; comparative ones ten or more.

Instructions change the plan, and the vendors say so. "Triggering is steerable through your system prompt" (Anthropic). "If you must keep effort low for latency, add targeted guidance like 'This task involves multistep reasoning. Think carefully before responding'" (Anthropic). "Think hard about this" flips the GPT-5 router (OpenAI). The Model Spec's efficiency rule is a guideline that "can be overridden implicitly" by context and user instruction.

"Check academia" is not a secret deeper mode. It changes the queries and the sources, as in section 2.4. The deeper modes are explicit features with their own switches and caps: Thinking, deep research, Claude Research, Google Deep Search, higher effort on the API. Saying "run extra loops" cannot push past `max_uses` or a plan's monthly cap.

### 4.3 Fair verdict

Bo is right about the incentives and about the consumer defaults: the cheap path is the default, the router and effort settings exist to save compute, and the deep modes are rationed by tier. He is wrong about the mechanism if the claim is that the model itself withholds research until forced. The vendors document a per-question decision, adjustable by instruction, plus explicit deep modes. The practical consequence is the same as his advice: say what depth you want, name the sources you want, pick the deep mode when it matters, and on the API set effort and search limits yourself.

### Plain-language answer (read aloud)

Bo is mostly right about the incentives. Every extra search and every second of thinking costs the company money, so free and cheap plans default to the quick path. OpenAI even describes a router that sends your question to a fast model unless it looks hard or you say "think hard about this". Deep research modes are limited to a few uses a month on cheaper plans. Where the claim goes too far is the idea that the model secretly holds back research. The documented behaviour is that the model decides per question whether it needs to search, based on whether the answer could be out of date, and you can change that decision by asking. On the API the default effort is high and developers set their own limits. Either way: say how deep you want it, name the sources, and pick the research mode when it matters.

### Sources for section 4

- Microsoft Learn, Azure OpenAI reasoning models (`reasoning_effort` values and defaults, `verbosity`), updated 20 August 2026: https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/reasoning
- OpenAI, "Reasoning models" guide: https://developers.openai.com/api/docs/guides/reasoning
- OpenAI, "Introducing GPT-5" (router and "think hard about this"), 7 August 2025: https://openai.com/index/introducing-gpt-5/
- OpenAI Model Spec, 18 August 2026 edition: https://model-spec.openai.com/2026-08-18.html
- OpenAI help, "Searching the web with ChatGPT": https://help.openai.com/en/articles/9237897-chatgpt-search
- OpenAI help, "Deep research in ChatGPT": https://help.openai.com/en/articles/10500283-deep-research-in-chatgpt ; limits via The Decoder, 25 April 2025: https://the-decoder.com/deep-research-feature-now-available-to-free-chatgpt-users/
- OpenAI help, GPT-5 in ChatGPT (plan limits): https://help.openai.com/en/articles/11909943-gpt-5-in-chatgpt
- Anthropic, effort parameter documentation: https://platform.claude.com/docs/en/build-with-claude/effort
- Anthropic, extended thinking documentation: https://platform.claude.com/docs/en/build-with-claude/extended-thinking
- Anthropic, web search tool documentation (when Claude searches, `max_uses`, pricing): https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool
- Anthropic help, "Usage limit best practices": https://support.claude.com/en/articles/9797557-usage-limit-best-practices
- Google, Gemini API thinking documentation: https://ai.google.dev/gemini-api/docs/thinking
- Search Engine Roundtable on Google's 80 percent cost reduction: https://www.seroundtable.com/google-sge-ai-answers-cost-80-less-37326.html
