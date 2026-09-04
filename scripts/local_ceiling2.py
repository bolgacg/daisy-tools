"""Answer recall on the offline index for the composed context (top page intro + best paragraphs), rule query and
title+BM25 page finding, no model."""
import json, re, sys, time
sys.path.insert(0, ".")
from daisy_tools import localwiki as lw, query as q, wiki as w
w.search, w.extracts, w.lookup, w.intro, w.paragraphs, w.find_pages_by_title = lw.search, lw.extracts, lw.lookup, lw.intro, lw.paragraphs, lw.find_pages_by_title
q.search, q.extracts = lw.search, lw.extracts
from daisy_tools.query import shaped_search
from daisy_tools.runner import compose_docs
def norm(s): return re.sub(r"[^a-z0-9æøå]+", " ", s.lower()).strip()
rows = [json.loads(l) for l in open(sys.argv[1] if len(sys.argv) > 1 else "data/daisy.jsonl", encoding="utf-8")]
hits = {"rule_composed": 0, "title_bm25_composed": 0, "title_bm25_top1_is_subject": 0}
t0 = time.time()
for i, r in enumerate(rows):
    gold = norm(r["Answer"])
    titles, used = shaped_search(r["Question"], limit=3)
    docs = compose_docs(r["Question"], titles, k=3, chars=900, page_fn=lw.paragraphs, intro_fn=lw.intro)
    hits["rule_composed"] += bool(gold) and gold in norm(" ".join(p for _, p in docs))
    th = lw.find_pages_by_title(r["Question"], limit=3)
    for t in titles:
        if t not in th: th.append(t)
    th = th[:3]
    docs2 = compose_docs(r["Question"], th, k=3, chars=900, page_fn=lw.paragraphs, intro_fn=lw.intro)
    hits["title_bm25_composed"] += bool(gold) and gold in norm(" ".join(p for _, p in docs2))
    hits["title_bm25_top1_is_subject"] += bool(th) and norm(th[0]).rstrip(" .") == norm(r["Subject"]).rstrip(" .")
    if (i + 1) % 200 == 0: print(i + 1, {k: round(v / (i + 1), 3) for k, v in hits.items()}, f"{time.time()-t0:.0f}s", flush=True)
n = len(rows); print("FINAL", json.dumps({k: round(v / n, 3) for k, v in hits.items()}), "n", n, f"{time.time()-t0:.0f}s")
