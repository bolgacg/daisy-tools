"""Answer recall with the offline index, no model: for each question, rule query -> top-3 pages; is the gold answer in
(a) the 3 intros (1200 chars), (b) the full 3 pages, (c) the top-3 reranked paragraphs? Also with the oracle query."""
import json, re, sys, time
sys.path.insert(0, ".")
from daisy_tools import localwiki as lw
from daisy_tools import query as q, wiki as w
w.search, w.extracts, w.lookup = lw.search, lw.extracts, lw.lookup; q.search, q.extracts = lw.search, lw.extracts
from daisy_tools.query import shaped_search
from daisy_tools.runner import rerank_paragraphs
def norm(s): return re.sub(r"[^a-z0-9æøå]+", " ", s.lower()).strip()
rows = [json.loads(l) for l in open(sys.argv[1] if len(sys.argv) > 1 else "data/daisy.jsonl", encoding="utf-8")]
hits = {k: 0 for k in ("rule_intro", "rule_page", "rule_rerank", "oracle_intro", "oracle_page", "oracle_rerank", "rule_top1_is_subject")}
t0 = time.time(); out = open("results/local_ceiling.jsonl", "w", encoding="utf-8")
for i, r in enumerate(rows):
    gold = norm(r["Answer"]); rec = {"id": r["id"]}
    for mode in ("rule", "oracle"):
        if mode == "rule":
            titles, used = shaped_search(r["Question"], limit=3)
        else:
            used = r["Subject"].rstrip("."); titles = lw.search(used, 3)
        intros = " ".join(lw.intro(t, 1200) for t in titles); pages = " ".join(lw.page(t) for t in titles)
        rer = " ".join(p for _, p in rerank_paragraphs(r["Question"], titles, k=3, chars=900, page_fn=lw.paragraphs))
        for name, text in (("intro", intros), ("page", pages), ("rerank", rer)):
            h = bool(gold) and gold in norm(text); hits[f"{mode}_{name}"] += h; rec[f"{mode}_{name}"] = h
        rec[f"{mode}_titles"] = titles; rec[f"{mode}_query"] = used
    hits["rule_top1_is_subject"] += bool(rec["rule_titles"]) and norm(rec["rule_titles"][0]).rstrip(" .") == norm(r["Subject"]).rstrip(" .")
    out.write(json.dumps(rec, ensure_ascii=False) + "\n")
    if (i + 1) % 100 == 0: print(i + 1, {k: round(v / (i + 1), 3) for k, v in hits.items()}, f"{time.time()-t0:.0f}s", flush=True)
n = len(rows); print("FINAL", json.dumps({k: round(v / n, 3) for k, v in hits.items()}), "n", n, f"{time.time()-t0:.0f}s")
