def score_length(text: str) -> float:
    n = len(text.strip())
    if n < 50:   return round(n / 50 * 0.3, 4)
    if n < 100:  return round(0.3 + (n - 50) / 50 * 0.4, 4)
    if n <= 1500: return 1.0
    if n <= 3000: return round(1.0 - (n - 1500) / 1500 * 0.4, 4)
    return 0.6