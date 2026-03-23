"""
evaluator.py
Scores LLM responses so the router can pick the "best" one in best-model mode.

Scoring heuristics (simple, fast, no extra API calls):
  - Length score    : longer responses (up to a ceiling) score higher
  - Coherence score : penalise very short or very long outputs
  - No-refusal score: penalise responses that contain refusal phrases
  - Unique-word ratio: rewards lexical variety

The final score is a float in [0, 1]. Higher is better.
"""

import re
from typing import Optional

# Common refusal / error phrases that indicate a low-quality response
_REFUSAL_PATTERNS = [
    r"i (can|cannot|can't|won't|am unable to)",
    r"as an ai",
    r"i don't have (the ability|access|information)",
    r"i'm sorry",
    r"i apologize",
    r"error",
    r"exception",
    r"failed",
    r"unfortunately",
]

_REFUSAL_RE = re.compile("|".join(_REFUSAL_PATTERNS), re.IGNORECASE)

# Ideal response length window (in words)
_IDEAL_MIN_WORDS = 30
_IDEAL_MAX_WORDS = 400


def score_response(response: Optional[str]) -> float:
    """
    Score a model response between 0.0 (worst) and 1.0 (best).
    Returns 0.0 for None or empty strings.
    """
    if not response or not response.strip():
        return 0.0

    words = response.split()
    word_count = len(words)

    # ── 1. Length score ────────────────────────────────────────────────────
    if word_count < _IDEAL_MIN_WORDS:
        length_score = word_count / _IDEAL_MIN_WORDS          # 0 → 1 linearly
    elif word_count <= _IDEAL_MAX_WORDS:
        length_score = 1.0
    else:
        # Penalise excessively long responses gradually
        overshoot = word_count - _IDEAL_MAX_WORDS
        length_score = max(0.3, 1.0 - overshoot / _IDEAL_MAX_WORDS)

    # ── 2. Refusal penalty ─────────────────────────────────────────────────
    refusal_hits = len(_REFUSAL_RE.findall(response))
    refusal_penalty = min(refusal_hits * 0.15, 0.6)           # cap at -0.6

    # ── 3. Lexical diversity ───────────────────────────────────────────────
    unique_ratio = len(set(w.lower() for w in words)) / max(word_count, 1)
    diversity_score = min(unique_ratio * 1.5, 1.0)            # scale up a bit

    # ── 4. Weighted combination ────────────────────────────────────────────
    raw_score = (
        length_score    * 0.50
        + diversity_score * 0.30
        - refusal_penalty * 0.20
    )

    return round(max(0.0, min(1.0, raw_score)), 4)


def pick_best(responses: dict[str, str]) -> tuple[str, str]:
    """
    Given {model_name: response_text}, return (best_model_name, best_response).
    Raises ValueError if the dict is empty.
    """
    if not responses:
        raise ValueError("No responses to evaluate.")

    scored = {name: score_response(text) for name, text in responses.items()}
    best_name = max(scored, key=scored.__getitem__)
    return best_name, responses[best_name]