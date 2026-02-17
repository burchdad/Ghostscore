"""
FICO8-style bin scoring model

This module implements explicit bucketed thresholds for each FICO factor
to increase realism compared with the default linear aggregator.

It exposes `aggregate_score(subscores, scorecard)` which returns a FICO
score in the 300-850 range using scorecard weights.
"""
from typing import Dict, List, Tuple
from ..scorecards import get_scorecard_weights

# Buckets map an upper-bound (inclusive) to a factor score (0-100).
# For utilization we express upper bounds as fractions (0.0-1.0).
UTILIZATION_BUCKETS: List[Tuple[float, int]] = [
    (0.01, 100),
    (0.09, 90),
    (0.29, 70),
    (0.49, 50),
    (0.74, 30),
    (1.00, 10),
]

# Payment history expressed as months since last late (lower is better).
PAYMENT_HISTORY_BUCKETS: List[Tuple[float, int]] = [
    (0.5, 10),   # very recent issue
    (6, 40),
    (12, 70),
    (36, 90),
    (99999, 100),
]

# Age of credit (years)
AGE_BUCKETS: List[Tuple[float, int]] = [
    (1, 20),
    (3, 50),
    (7, 75),
    (15, 95),
    (99999, 100),
]

# New credit (inquiries / new accounts) - lower is better
NEW_CREDIT_BUCKETS: List[Tuple[float, int]] = [
    (0, 100),
    (1, 85),
    (2, 65),
    (4, 45),
    (99999, 20),
]

# Credit mix: coarse buckets
MIX_BUCKETS: List[Tuple[float, int]] = [
    (0.0, 20),
    (1.0, 60),
    (2.0, 85),
    (99999, 100),
]


def _bucket_score(value: float, buckets: List[Tuple[float, int]]) -> int:
    """Return the bucketed score (0-100) for a value using bucket list."""
    for bound, score in buckets:
        if value <= bound:
            return score
    return buckets[-1][1]


def _normalize_subscores(subscores: Dict[str, float]) -> Dict[str, float]:
    """Convert raw subscores or feature-like inputs into bucketed 0-100 scores.

    Expects subscores keys: 'utilization' (0-100 percentage), 'payment_history'
    (months since last late or severity proxy), 'age' (years), 'new_credit' (count),
    'mix' (count of account types or a small numeric proxy).
    """
    out = {}

    # Utilization: subscores may be 0-100 (percent). Convert to fraction.
    util = subscores.get('utilization', 50)
    util_frac = max(0.0, min(100.0, util)) / 100.0
    out['utilization'] = _bucket_score(util_frac, UTILIZATION_BUCKETS)

    # Payment history: if provided as months since last late, use buckets.
    ph = subscores.get('payment_history', 50)
    # If ph looks like a 0-100 subscore rather than months, translate roughly
    if ph > 20:  # assume 0-100 score -> convert to months proxy (inverse)
        months_proxy = max(0.0, (100 - ph) / 2.0)
    else:
        months_proxy = float(ph)
    out['payment_history'] = _bucket_score(months_proxy, PAYMENT_HISTORY_BUCKETS)

    # Age: subscores may be 0-100 or years
    age = subscores.get('age', 50)
    if age > 20:  # interpret as 0-100 subscore -> convert to years proxy
        years = max(0.5, (age / 10.0))
    else:
        years = float(age)
    out['age'] = _bucket_score(years, AGE_BUCKETS)

    # New credit: treat as count/inquiries
    nc = subscores.get('new_credit', 50)
    if nc > 10:
        nc_count = nc
    else:
        # assume 0-100 subscore -> invert to small count proxy
        nc_count = max(0.0, 5 - (nc / 25.0))
    out['new_credit'] = _bucket_score(nc_count, NEW_CREDIT_BUCKETS)

    # Mix: use provided number-of-types or 0-100 subscore
    mix = subscores.get('mix', 50)
    if mix > 10:
        mix_count = min(3, int(round(mix / 33.0)))
    else:
        mix_count = mix
    out['mix'] = _bucket_score(mix_count, MIX_BUCKETS)

    return out


MIN_SCORE = 300
MAX_SCORE = 850
MIDPOINT_SCORE = 575


def aggregate_score(subscores: Dict[str, float], scorecard: str) -> int:
    """Aggregate bucketed subscores into a final FICO score using weights.

    This function mirrors the signature of the existing `aggregator.aggregate_score`
    so the `FicoEngine` can optionally call it when `model='fico8'`.
    """
    weights = get_scorecard_weights(scorecard)

    # Convert incoming subscores into bucketed 0-100 values
    bucketed = _normalize_subscores(subscores)

    weighted_sum = 0.0
    weight_total = 0.0
    for factor, weight in weights.items():
        if factor in bucketed:
            val = bucketed[factor]
            weighted_sum += val * weight
            weight_total += weight

    weighted_avg = weighted_sum / weight_total if weight_total > 0 else 50.0

    # Map weighted_avg (0-100) to 300-850 using same curve as default aggregator
    if weighted_avg <= 50:
        fico_score = MIN_SCORE + (weighted_avg / 50.0) * (MIDPOINT_SCORE - MIN_SCORE)
    else:
        fico_score = MIDPOINT_SCORE + ((weighted_avg - 50.0) / 50.0) * (MAX_SCORE - MIDPOINT_SCORE)

    return int(round(fico_score))
