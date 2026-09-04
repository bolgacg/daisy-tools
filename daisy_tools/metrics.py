"""Scoring identical to SDU-Daisy/evaluation/eval.py (EM, token F1, BLEU with smoothing method4).
Kept byte-for-byte in behaviour so our numbers are comparable with the group's own tables."""
import re

def normalize_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)  # NOTE: their normaliser strips æøå too; we keep it identical
    return s.strip()

def f1_score(prediction: str, ground_truth: str) -> float:
    pred_tokens = normalize_text(prediction).split()
    gold_tokens = normalize_text(ground_truth).split()
    common = set(pred_tokens) & set(gold_tokens)
    num_same = sum(min(pred_tokens.count(w), gold_tokens.count(w)) for w in common)
    if len(pred_tokens) == 0 or len(gold_tokens) == 0:
        return float(pred_tokens == gold_tokens)
    if num_same == 0:
        return 0.0
    precision = num_same / len(pred_tokens)
    recall = num_same / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)

def exact_match_score(prediction: str, ground_truth: str) -> float:
    return float(normalize_text(prediction) == normalize_text(ground_truth))

def bleu_score(prediction: str, ground_truth: str) -> float:
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    pred_tokens = normalize_text(prediction).split()
    gold_tokens = normalize_text(ground_truth).split()
    return sentence_bleu([gold_tokens], pred_tokens, smoothing_function=SmoothingFunction().method4)

def score_all(pairs, with_bleu=True):
    """pairs: iterable of (prediction, gold). Returns dict of means."""
    ems, f1s, bleus = [], [], []
    for pred, gold in pairs:
        pred = "" if pred is None else str(pred)
        ems.append(exact_match_score(pred, gold)); f1s.append(f1_score(pred, gold))
        if with_bleu:
            bleus.append(bleu_score(pred, gold))
    n = max(len(ems), 1)
    out = {"EM": sum(ems) / n, "F1": sum(f1s) / n, "n": len(ems)}
    if with_bleu:
        out["BLEU"] = sum(bleus) / n
    return out

# Their prompt, verbatim (evaluation/eval.py PROMPT_TEMPLATE)
PROMPT_TEMPLATE = """
Besvar spørgsmålet med kun det direkte svar, uden forklaring om hvorfor.
Regelsæt:
- Svar kun på dansk.
- Hvis svaret er i højde, svar i meter (m).
- Hvis svaret er i vægt, svar i kilogram (kg).
- Hvis svaret er om en størrelse, svar i centimeter (cm). Fx Hvor stort er maleriet Mona Lisa? Svar: 77 cm x 53 cm.
- Hvis svaret er en person angiv den måde de typisk bliver angivet på i danske tekster.

\n\nSpørgsmål: {question}\nSvar:"""


def lenient_match(prediction: str, ground_truth: str) -> float:
    """1 if the normalised gold appears inside the normalised prediction (format-tolerant EM)."""
    p, g = normalize_text(prediction or ""), normalize_text(ground_truth or "")
    return float(bool(g) and g in p)


# The same prompt as used by the group's own Inspect task (dfm-evals/dfm_evals/tasks/daisy.py, max_gen_toks 100,
# temperature 0). Differs from eval.py only in the leading newline and the blank line before "Spørgsmål".
PROMPT_TEMPLATE_DFM = """Besvar spørgsmålet med kun det direkte svar, uden forklaring om hvorfor.
Regelsæt:
- Svar kun på dansk.
- Hvis svaret er i højde, svar i meter (m).
- Hvis svaret er i vægt, svar i kilogram (kg).
- Hvis svaret er om en størrelse, svar i centimeter (cm). Fx Hvor stort er maleriet Mona Lisa? Svar: 77 cm x 53 cm.
- Hvis svaret er en person angiv den måde de typisk bliver angivet på i danske tekster.

Spørgsmål: {question}
Svar:"""
