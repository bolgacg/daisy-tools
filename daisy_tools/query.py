"""Turn a Danish question into a search query the Wikipedia search engine answers.
Full questions often return zero hits (every term is required); we strip question words and
back off by dropping the least specific terms until something is found."""
import re
from .wiki import search, extracts

STOP = set("""hvem hvad hvor hvornår hvilket hvilken hvilke hvordan hvorfor hvis er var blev bliver
har havde have i på af til fra med om og eller at det den de der som en et for ved under over
mellem efter før sin sit sine hans hendes dens dets man kan skal ikke også år årstal navn navnet
kaldes kaldet hedder hed skrev skrevet udgivet udkom første sidste hvilket hvilken""".split())

def keywords(question: str):
    toks = re.findall(r"[0-9A-Za-zÆØÅæøå\-']+", question)
    kept = [t for t in toks if t.lower() not in STOP and len(t) > 1]
    # keep capitalised and numeric tokens first (names, years), then the rest, preserving order
    prio = [t for t in kept if t[0].isupper() or t[0].isdigit()]
    rest = [t for t in kept if t not in prio]
    return prio + rest

def shaped_search(question: str, limit=3, max_backoff=4):
    """Try the full question, then keyword sets of shrinking size. Returns (titles, query_used)."""
    tries = [question]
    kw = keywords(question)
    for k in range(len(kw), max(len(kw) - max_backoff, 1) - 1, -1):
        tries.append(" ".join(kw[:k]))
    seen = set()
    for q in tries:
        if q in seen or not q.strip():
            continue
        seen.add(q)
        titles = search(q, limit)
        if titles:
            return titles, q
    return [], tries[-1]

def shaped_lookup(question: str, limit=3, chars=1200):
    titles, q = shaped_search(question, limit)
    ex = extracts(titles, chars)
    return [(t, ex.get(t, "")) for t in titles], q
