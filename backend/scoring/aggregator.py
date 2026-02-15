"""
Aggregation Layer

Combines individual factor scores into a final FICO score
using scorecard-specific weights.
"""

from typing import Dict
from .scorecards import get_scorecard_weights


# Score range parameters
MIN_SCORE = 300
MAX_SCORE = 850
MIDPOINT_SCORE = 575  # Below this represents poor credit


def aggregate_score(
    subscores: Dict[str, float],
    scorecard: str
) -> int:
    """
    Combine weighted factor subscores into final FICO score.
    
    The real FICO model uses a complex curve fitting algorithm.
    We use a simplified linear model for MVP:
    
      1. Get weights for this scorecard
      2. Calculate weighted average (0-100)
      3. Scale to FICO range (300-850)
    
    Args:
        subscores: Dict with keys like 'payment_history', 'utilization', etc.
                   Values should be 0-100
        scorecard: Scorecard type for weight selection
        
    Returns:
        Final FICO-equivalent score (300-850)
    """
    
    # Get scorecard-specific weights
    weights = get_scorecard_weights(scorecard)
    
    # Calculate weighted average (0-100)
    weighted_sum = 0.0
    weight_total = 0.0
    
    for factor, weight in weights.items():
        if factor in subscores:
            score_value = subscores[factor]
            # Ensure score is in 0-100 range
            score_value = max(0, min(100, score_value))
            weighted_sum += score_value * weight
            weight_total += weight
    
    # Normalize if not all factors present
    weighted_avg = weighted_sum / weight_total if weight_total > 0 else 50
    
    # Scale from 0-100 to 300-850 range
    # Using a curve that maps:
    #   0   → 300
    #   50  → 575
    #   100 → 850
    
    if weighted_avg <= 50:
        # Lower half: 0-50 maps to 300-575
        fico_score = MIN_SCORE + (weighted_avg / 50) * (MIDPOINT_SCORE - MIN_SCORE)
    else:
        # Upper half: 50-100 maps to 575-850
        fico_score = MIDPOINT_SCORE + ((weighted_avg - 50) / 50) * (MAX_SCORE - MIDPOINT_SCORE)
    
    # Round to nearest integer
    return int(round(fico_score))


def calculate_score_details(
    subscores: Dict[str, float],
    scorecard: str,
    final_score: int
) -> Dict:
    """
    Generate detailed score breakdown for user display.
    
    Args:
        subscores: Individual factor scores (0-100)
        scorecard: Scorecard type
        final_score: Final FICO score
        
    Returns:
        Dict with score breakdown and explanations
    """
    
    weights = get_scorecard_weights(scorecard)
    
    # Score impact rankings
    score_impacts = []
    for factor, weight in weights.items():
        if factor in subscores:
            impact_points = weight * 100  # Max impact for this factor
            score_impacts.append({
                "factor": factor,
                "score": subscores[factor],
                "weight": weight,
                "max_impact": impact_points,
            })
    
    # Sort by weight (importance)
    score_impacts.sort(key=lambda x: x["weight"], reverse=True)
    
    return {
        "final_score": final_score,
        "scorecard": scorecard,
        "subscores": subscores,
        "weights": weights,
        "score_impacts": score_impacts,
    }


def estimate_score_range_improvement(
    current_subscores: Dict[str, float],
    current_scorecard: str,
    improvement_factor: str,
    improvement_amount: float
) -> Dict:
    """
    Estimate how much a score could improve if a factor improves.
    
    Used for "what-if" scenarios and recommendations.
    
    Args:
        current_subscores: Current factor scores
        current_scorecard: Current scorecard
        improvement_factor: Which factor to improve (e.g., "utilization")
        improvement_amount: How much (0.0-100.0 points)
        
    Returns:
        Dict with current score and estimated improved score
    """
    
    current_score = aggregate_score(current_subscores, current_scorecard)
    
    # Simulate improvement
    improved_subscores = current_subscores.copy()
    if improvement_factor in improved_subscores:
        improved_subscores[improvement_factor] = min(
            100,
            improved_subscores[improvement_factor] + improvement_amount
        )
    
    improved_score = aggregate_score(improved_subscores, current_scorecard)
    
    return {
        "current_score": current_score,
        "improved_score": improved_score,
        "estimated_gain": improved_score - current_score,
        "factor": improvement_factor,
    }
