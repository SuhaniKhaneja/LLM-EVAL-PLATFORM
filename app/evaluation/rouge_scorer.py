from rouge_score import rouge_scorer as rs

_scorer = rs.RougeScorer(["rouge1"], use_stemmer=True)

def score_rouge1(hypothesis: str, reference: str) -> float:
    if not reference.strip():
        return 1.0
    result = _scorer.score(reference, hypothesis)
    return round(result["rouge1"].fmeasure, 4)