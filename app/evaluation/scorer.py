
from dataclasses import dataclass

from app.evaluation.length_scorer import score_length
from app.evaluation.rouge_scorer import (
    score_rouge1,
    score_rouge_l,
    score_bleu,
)
from app.evaluation.toxicity_checker import check_toxicity


# Existing weights retained to avoid changing the meaning of the
# overall score during this upgrade.
_W = {
    "length": 0.25,
    "rouge1": 0.40,
    "toxicity": 0.35,
}


@dataclass
class CompositeScore:
    length_score: float
    rouge1_score: float | None
    rouge_l_score: float | None
    bleu_score: float | None
    toxicity_score: float
    is_toxic: bool
    overall_score: float


def compute_scores(response: str, reference: str = "") -> CompositeScore:
    length = score_length(response)
    toxicity = check_toxicity(response)

    # Reference-based metrics are unavailable without a reference.
    rouge1 = score_rouge1(response, reference)
    rouge_l = score_rouge_l(response, reference)
    bleu = score_bleu(response, reference)

    if rouge1 is not None:
        overall = (
            length * _W["length"]
            + rouge1 * _W["rouge1"]
            + toxicity.score * _W["toxicity"]
        ) * 100
    else:
        # Normalize the available weights when no reference is provided.
        available_weight = _W["length"] + _W["toxicity"]
        overall = (
            length * _W["length"]
            + toxicity.score * _W["toxicity"]
        ) / available_weight * 100

    return CompositeScore(
        length_score=length,
        rouge1_score=rouge1,
        rouge_l_score=rouge_l,
        bleu_score=bleu,
        toxicity_score=toxicity.score,
        is_toxic=toxicity.is_toxic,
        overall_score=round(overall, 2),
    )
