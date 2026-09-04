"""Offline Danish Wikipedia: a SQLite FTS5 index of the wikimedia/wikipedia 20231101.da dump (plain text).
Same interface as wiki.py (search, extracts, lookup) plus page access and paragraph splitting for reranking.
Build with scripts/build_localwiki.py; the DB path defaults to ~/data/dawiki/dawiki.sqlite."""
import os, re, sqlite3, threading
DB = os.environ.get("DAWIKI_DB", os.path.expanduser("~/data/dawiki/dawiki.sqlite"))
_local = threading.local()
def con():
    """One SQLite connection per thread: a shared connection breaks under the runner's worker threads."""
    c = getattr(_local, "con", None)
    if c is None:
        c = sqlite3.connect(DB, check_same_thread=False); _local.con = c
    return c

def _fts_query(q):
    toks = re.findall(r"[0-9A-Za-zÆØÅæøå]+", q)
    return " OR ".join(f'"{t}"' for t in toks[:16]) if toks else '""'

def search(query, limit=3):
    """Titles of the best-matching pages (BM25 over title and text, title weighted)."""
    try:
        rows = con().execute("SELECT title FROM pages WHERE pages MATCH ? ORDER BY bm25(pages, 10.0, 1.0) LIMIT ?", (_fts_query(query), limit)).fetchall()
    except sqlite3.OperationalError:
        return []
    return [r[0] for r in rows]

def page(title):
    r = con().execute("SELECT text FROM pages WHERE title = ? LIMIT 1", (title,)).fetchone()
    return r[0] if r else ""

def intro(title, chars=1200):
    t = page(title)
    return t[:chars]

def paragraphs(title, min_chars=80):
    return [p.strip() for p in page(title).split("\n") if len(p.strip()) >= min_chars]

def extracts(titles, chars=1200):
    return {t: intro(t, chars) for t in titles}

def lookup(query, limit=3, chars=1200):
    titles = search(query, limit)
    return [(t, intro(t, chars)) for t in titles]



def title_candidates(question, max_len=7):
    """Quoted spans first, then every n-gram (longest first) that starts at a capitalised token; Danish titles keep
    lowercase inner words ("De levendes Land", "Et selskab af danske kunstnere i Rom"), so inner words are unrestricted."""
    cands = []
    for m in re.finditer(r"[\"“„»«']([^\"”“„»«']{3,80})[\"”“»«']", question):
        cands.append(m.group(1).strip())
    words = re.findall(r"[0-9A-Za-zÆØÅæøå'\-\.]+", question.rstrip("?.!"))
    n = len(words)
    for L in range(min(max_len, n), 0, -1):
        for i in range(0, n - L + 1):
            span = words[i:i + L]
            if not span[0][:1].isupper():
                continue
            if i == 0 and L == 1:
                continue  # the question word itself
            cands.append(" ".join(span).rstrip(",;:."))
    seen = set(); out = []
    for c in cands:
        k = c.lower()
        if k and k not in seen:
            seen.add(k); out.append(c)
    return out

def find_pages_by_title(question, limit=3):
    """Exact (case-insensitive) title matches for the question's spans, longest first, via the indexed titles table."""
    hits = []
    cur = con()
    for c in title_candidates(question):
        if len(c) < 4 or any(c.lower() in h.lower() for h in hits):
            continue  # too short, or already inside a longer hit
        r = cur.execute("SELECT title FROM titles WHERE title_lower = ? LIMIT 1", (c.lower(),)).fetchone()
        if r and r[0] not in hits:
            hits.append(r[0])
        if len(hits) >= limit:
            break
    return hits
