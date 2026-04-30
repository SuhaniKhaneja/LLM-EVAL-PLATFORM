import re
from dataclasses import dataclass

_TOXIC = [
    r"\b(kill|murder)\s+(yourself|himself|herself)\b",
    r"\b(n[i1]gg[ae]r|k[i1]ke|sp[i1]c)\b",
    r"\b(make|build)\s+a?\s*(bomb|explosive)\b",
    r"\bhow\s+to\s+(hack|ddos)\b",
]
_COMPILED = [re.compile(p, re.IGNORECASE) for p in _TOXIC]

@dataclass
class ToxicityResult:
    score: float
    is_toxic: bool

def check_toxicity(text: str) -> ToxicityResult:
    for p in _COMPILED:
        if p.search(text):
            return ToxicityResult(score=0.0, is_toxic=True)
    return ToxicityResult(score=1.0, is_toxic=False)