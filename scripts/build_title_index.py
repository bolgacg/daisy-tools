"""Add an indexed titles table to the offline Danish Wikipedia DB (exact title lookup in microseconds)."""
import os, sqlite3, time
import pyarrow.parquet as pq
D = os.path.expanduser("~/data/dawiki"); db = os.path.join(D, "dawiki.sqlite")
con = sqlite3.connect(db); t0 = time.time()
con.execute("DROP TABLE IF EXISTS titles"); con.execute("CREATE TABLE titles(title_lower TEXT PRIMARY KEY, title TEXT)")
n = 0
for f in ["train-00000-of-00002.parquet", "train-00001-of-00002.parquet"]:
    tbl = pq.read_table(os.path.join(D, f), columns=["title"])
    rows = [(t.lower(), t) for t in tbl.column("title").to_pylist()]
    con.executemany("INSERT OR IGNORE INTO titles(title_lower, title) VALUES (?, ?)", rows); con.commit(); n += len(rows)
print("titles indexed", n, round(time.time() - t0), "s")
for q in ["de levendes land", "storebæltsforbindelsen", "et selskab af danske kunstnere i rom"]:
    print(q, "->", con.execute("SELECT title FROM titles WHERE title_lower = ?", (q,)).fetchone())
