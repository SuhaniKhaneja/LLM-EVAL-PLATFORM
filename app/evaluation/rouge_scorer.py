
from rouge_score import rouge_scorer as rs
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

_scorer = rs.RougeScorer(
    ["rouge1", "rougeL"],
    use_stemmer=True,
)

_smoothing = SmoothingFunction().method1


def score_rouge1(hypothesis: str, reference: str) -> float | None:
    if not reference or not reference.strip():
        return None

    if not hypothesis or not hypothesis.strip():
        return 0.0

    result = _scorer.score(reference, hypothesis)
    return round(result["rouge1"].fmeasure, 4)


def score_rouge_l(hypothesis: str, reference: str) -> float | None:
    if not reference or not reference.strip():
        return None

    if not hypothesis or not hypothesis.strip():
        return 0.0

    result = _scorer.score(reference, hypothesis)
    return round(result["rougeL"].fmeasure, 4)


def score_bleu(hypothesis: str, reference: str) -> float | None:
    if not reference or not reference.strip():
        return None

    if not hypothesis or not hypothesis.strip():
        return 0.0

    reference_tokens = reference.lower().split()
    hypothesis_tokens = hypothesis.lower().split()

    score = sentence_bleu(
        [reference_tokens],
        hypothesis_tokens,
        smoothing_function=_smoothing,
    )

    return round(score, 4)
