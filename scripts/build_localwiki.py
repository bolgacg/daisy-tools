"""Build ~/data/dawiki/dawiki.sqlite (FTS5, BM25) from the Hugging Face wikimedia/wikipedia 20231101.da parquet files."""
import os, sqlite3, sys, time, urllib.request
import pyarrow.parquet as pq
D = os.path.expanduser("~/data/dawiki"); os.makedirs(D, exist_ok=True)
FILES = ["train-00000-of-00002.parquet", "train-00001-of-00002.parquet"]
BASE = "https://huggingface.co/datasets/wikimedia/wikipedia/resolve/main/20231101.da/"
for f in FILES:
    p = os.path.join(D, f)
    if not os.path.exists(p):
        print("downloading", f, flush=True); urllib.request.urlretrieve(BASE + f, p)
db = os.path.join(D, "dawiki.sqlite")
if os.path.exists(db): os.remove(db)
con = sqlite3.connect(db)
con.execute("CREATE VIRTUAL TABLE pages USING fts5(title, text, tokenize='unicode61 remove_diacritics 0')")
t0 = time.time(); n = 0
for f in FILES:
    tbl = pq.read_table(os.path.join(D, f), columns=["title", "text"])
    for batch in tbl.to_batches(20000):
        rows = list(zip(batch.column("title").to_pylist(), batch.column("text").to_pylist()))
        con.executemany("INSERT INTO pages(title, text) VALUES (?, ?)", rows); con.commit(); n += len(rows)
        print(n, "pages", round(time.time() - t0), "s", flush=True)
con.execute("INSERT INTO pages(pages) VALUES('optimize')"); con.commit()
print("done", n, "pages ->", db, round(os.path.getsize(db) / 1e9, 2), "GB", flush=True)
q = 'SELECT title FROM pages WHERE pages MATCH ? ORDER BY bm25(pages, 10.0, 1.0) LIMIT 3'
for query in ['"De" OR "levendes" OR "Land"', '"Storebæltsforbindelsen"', '"Grundtvig" OR "salme"']:
    print(query, "->", [r[0] for r in con.execute(q, (query,)).fetchall()])
