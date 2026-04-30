from dataclasses import dataclass
from app.evaluation.length_scorer import score_length
from app.evaluation.rouge_scorer import score_rouge1
from app.evaluation.toxicity_checker import check_toxicity

_W = {"length": 0.25, "rouge1": 0.40, "toxicity": 0.35}

@dataclass
class CompositeScore:
    length_score: float
    rouge1_score: float
    toxicity_score: float
    is_toxic: bool
    overall_score: float   # 0–100

def compute_scores(response: str, reference: str = "") -> CompositeScore:
    ls = score_length(response)
    rs = score_rouge1(response, reference or response[:80])
    tc = check_toxicity(response)
    overall = round(
        (ls * _W["length"] + rs * _W["rouge1"] + tc.score * _W["toxicity"]) * 100, 2
    )
    return CompositeScore(
        length_score=ls, rouge1_score=rs,
        toxicity_score=tc.score, is_toxic=tc.is_toxic,
        overall_score=overall
    )