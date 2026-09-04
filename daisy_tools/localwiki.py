"""Offline Danish Wikipedia: a SQLite FTS5 index of the wikimedia/wikipedia 20231101.da dump (plain text).
Same interface as wiki.py (search, extracts, lookup) plus page access and paragraph splitting for reranking.
Build with scripts/build_localwiki.py; the DB path defaults to ~/data/dawiki/dawiki.sqlite."""
import os, re, sqlite3
DB = os.environ.get("DAWIKI_DB", os.path.expanduser("~/data/dawiki/dawiki.sqlite"))
_con = None
def con():
    global _con
    if _con is None:
        _con = sqlite3.connect(DB, check_same_thread=False)
    return _con

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
