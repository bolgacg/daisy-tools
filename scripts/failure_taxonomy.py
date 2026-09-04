"""Rule-based failure taxonomy with counts, per run: where do wrong answers come from?
Categories (first match wins): exact; format (contains-gold but not exact); refused ("ved ikke"/"ikke nævnt"/"kan ikke");
empty; year-near (a year within 5 of a year gold); year-far; copied-title (prediction equals a fetched title, not gold);
default-answer (one of the run's three most repeated predictions); other-wrong."""
import glob, json, re, sys, collections
sys.path.insert(0, ".")
from daisy_tools.metrics import exact_match_score as em, lenient_match as lm, normalize_text as nt
REFUSE = re.compile(r"ved (det )?ikke|ikke nævnt|kan ikke|ikke oplyst|ukendt|ingen oplysning|not (mentioned|found|known)|i don't know|unknown", re.I)
def year(s):
    m = re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", s or ""); return int(m.group(1)) if m else None
def taxonomy(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    freq = collections.Counter(nt(r["prediction"]) for r in rows); defaults = {k for k, _ in freq.most_common(3) if k}
    c = collections.Counter()
    for r in rows:
        p, g = r["prediction"], r["gold"]
        if em(p, g) >= 1: c["exact"] += 1; continue
        if lm(p, g) >= 1: c["format (contains gold)"] += 1; continue
        if not p.strip(): c["empty"] += 1; continue
        if REFUSE.search(p): c["refused / not found"] += 1; continue
        gy, py = year(g), year(p)
        if gy and g.strip().isdigit():
            if py is not None: c["year within 5" if abs(py - gy) <= 5 else "year off by more"] += 1
            else: c["no year given"] += 1
            continue
        if r.get("titles") and any(nt(t) == nt(p) for t in r["titles"]): c["copied a fetched title"] += 1; continue
        if nt(p) in defaults: c["default answer"] += 1; continue
        c["other wrong entity"] += 1
    return len(rows), c
if __name__ == "__main__":
    paths = sys.argv[1:] or sorted(glob.glob("results/pred_*_closed.jsonl") + glob.glob("results/pred_*_retrieve.jsonl") + glob.glob("results/pred_*_agentic.jsonl"))
    cats = ["exact", "format (contains gold)", "refused / not found", "empty", "year within 5", "year off by more", "no year given", "copied a fetched title", "default answer", "other wrong entity"]
    print("| run | n | " + " | ".join(cats) + " |\n|---|---|" + "---|" * len(cats))
    for p in paths:
        n, c = taxonomy(p); name = p.replace("results/pred_", "").replace(".jsonl", "")
        print(f"| {name} | {n} | " + " | ".join(str(c.get(k, 0)) for k in cats) + " |")
