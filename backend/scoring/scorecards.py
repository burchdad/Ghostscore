"""
Scorecard Segmentation Layer

Analyzes profile features to assign a scorecard segment.
Real FICO uses 15+ different scorecards. We use 4 for MVP:
  - derogatory: Has serious marks (bankruptcies, charge-offs)
  - thin: Too few accounts (limited history)
  - young: Recent credit (avg age < 2 years)
  - clean: Standard profile
"""

from typing import Dict, Any, Literal


def determine_scorecard(
    profile: Dict[str, Any],
    features: Dict[str, float]
) -> Literal["derogatory", "thin", "young", "clean"]:
    """
    Determine which scorecard segment the profile fits.
    
    Assigning to the right scorecard allows us to apply
    customized weights for different credit profiles.
    
    Args:
        profile: Raw credit profile
        features: Normalized features from feature_engine
        
    Returns:
        Scorecard type: "derogatory", "thin", "young", or "clean"
    """
    
    # Priority 1: Derogatory marks take precedence
    if features.get("bankruptcy_count", 0) > 0:
        return "derogatory"
    
    if features.get("charge_off_count", 0) > 0:
        return "derogatory"
    
    # Collections within 3 years are treated as derogatory
    if (features.get("collection_count", 0) > 0 and 
        features.get("days_since_derogatory", 999999) < 365 * 3):
        return "derogatory"
    
    # Priority 2: Thin file (insufficient history)
    if features.get("total_accounts", 0) <= 3:
        return "thin"
    
    # Priority 3: Young credit (recent opener)
    if features.get("avg_age", 0) < 2.0:
        return "young"
    
    # Default: Clean profile
    return "clean"


def get_scorecard_weights(scorecard: str) -> Dict[str, float]:
    """
    Get factor weights for a specific scorecard.
    
    Different scorecards emphasize different factors.
    Real FICO has ~270 different scorecards with unique weights.
    
    Args:
        scorecard: One of "derogatory", "thin", "young", "clean"
        
    Returns:
        Dict of factor weights (should sum to 1.0)
    """
    
    # Base weights (clean profile)
    base_weights = {
        'payment_history': 0.35,
        'utilization': 0.30,
        'age': 0.15,
        'new_credit': 0.10,
        'mix': 0.10,
    }
    
    if scorecard == "derogatory":
        # Payment history becomes even more important
        return {
            'payment_history': 0.50,
            'utilization': 0.20,
            'age': 0.15,
            'new_credit': 0.10,
            'mix': 0.05,
        }
    
    elif scorecard == "thin":
        # Age and mix matter less; payment history still key
        return {
            'payment_history': 0.45,
            'utilization': 0.30,
            'age': 0.10,
            'new_credit': 0.10,
            'mix': 0.05,
        }
    
    elif scorecard == "young":
        # Mix and new credit more important for young profiles
        return {
            'payment_history': 0.30,
            'utilization': 0.30,
            'age': 0.10,
            'new_credit': 0.15,
            'mix': 0.15,
        }
    
    # "clean" or default
    return base_weights


def get_scorecard_description(scorecard: str) -> str:
    """Get human-readable description of scorecard."""
    descriptions = {
        "derogatory": "Profile with serious credit marks (bankruptcy, charge-off, recent collection)",
        "thin": "Thin file - too few accounts or limited credit history",
        "young": "Young profile - recent credit opener",
        "clean": "Standard clean profile",
    }
    return descriptions.get(scorecard, "Unknown profile type")
