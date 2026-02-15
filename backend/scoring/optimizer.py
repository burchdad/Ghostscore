"""
Scenario Optimization Layer

Finds the best credit improvement actions for a user.
This is the core of GhostScore's advice engine.
"""

from typing import Dict, List, Any
from copy import deepcopy
from .feature_engine import extract_features
from .scorecards import determine_scorecard


def find_best_actions(
    profile: Dict[str, Any],
    calculate_score_func
) -> List[Dict[str, Any]]:
    """
    Find the most impactful actions to improve credit score.
    
    Simulates paying down each account and ranks actions by impact.
    
    Args:
        profile: Credit profile dict
        calculate_score_func: Function (profile) -> score that calculates FICO
        
    Returns:
        List of recommendations sorted by estimated score gain
    """
    
    try:
        original_score = calculate_score_func(profile)
    except Exception:
        original_score = 650
    
    recommendations = []
    accounts = profile.get("accounts", [])
    
    # === PAYDOWN RECOMMENDATIONS ===
    for account in accounts:
        # Only optimize revolving accounts (credit cards)
        if account.get("type") != "credit_card":
            continue
        
        balance = float(account.get("balance", 0))
        limit = float(account.get("limit", 1))
        
        if limit == 0:
            continue
        
        # Target: 9% utilization (proven sweet spot)
        target_balance = limit * 0.09
        
        if balance <= target_balance:
            continue  # Already optimized
        
        paydown_amount = balance - target_balance
        
        # Simulate paydown
        simulated = deepcopy(profile)
        for sim_acc in simulated.get("accounts", []):
            if sim_acc.get("id") == account.get("id"):
                sim_acc["balance"] = target_balance
                break
        
        try:
            new_score = calculate_score_func(simulated)
            gain = new_score - original_score
        except Exception:
            gain = 0
        
        if gain > 0:
            recommendations.append({
                "type": "paydown",
                "priority": "high" if gain > 30 else "medium" if gain > 15 else "low",
                "account_id": account.get("id"),
                "account_name": account.get("name", "Unknown Account"),
                "account_type": account.get("type"),
                "current_balance": balance,
                "target_balance": target_balance,
                "paydown_amount": paydown_amount,
                "estimated_score_gain": gain,
            })
    
    # === CLOSE/PAY OFF RECOMMENDATIONS ===
    for account in accounts:
        if account.get("type") not in ("credit_card", "personal_loan"):
            continue
        
        balance = float(account.get("balance", 0))
        
        if balance <= 0:
            continue  # Already paid off
        
        # Simulate paying off completely
        simulated = deepcopy(profile)
        for sim_acc in simulated.get("accounts", []):
            if sim_acc.get("id") == account.get("id"):
                sim_acc["balance"] = 0
                break
        
        try:
            new_score = calculate_score_func(simulated)
            gain = new_score - original_score
        except Exception:
            gain = 0
        
        if gain > 20:  # Only recommend if significant gain
            recommendations.append({
                "type": "payoff",
                "priority": "high" if gain > 40 else "medium" if gain > 20 else "low",
                "account_id": account.get("id"),
                "account_name": account.get("name", "Unknown Account"),
                "account_type": account.get("type"),
                "current_balance": balance,
                "target_balance": 0,
                "paydown_amount": balance,
                "estimated_score_gain": gain,
            })
    
    # === DEROGATORY REMOVAL (if applicable) ===
    derogatories = profile.get("derogatories", [])
    if derogatories:
        # Estimate score gain if all derogatories removed
        simulated = deepcopy(profile)
        simulated["derogatories"] = []
        
        try:
            new_score = calculate_score_func(simulated)
            gain = new_score - original_score
        except Exception:
            gain = 0
        
        if gain > 0:
            derog_summary = {}
            for d in derogatories:
                d_type = d.get("type", "unknown")
                derog_summary[d_type] = derog_summary.get(d_type, 0) + 1
            
            recommendations.append({
                "type": "derogatory_removal",
                "priority": "high",
                "description": f"Remove {len(derogatories)} derogatory mark(s)",
                "derogatory_breakdown": derog_summary,
                "estimated_score_gain": gain,
                "note": "Derogatory marks can be disputed or may age out.",
            })
    
    # Sort by score gain (descending)
    recommendations.sort(
        key=lambda x: x.get("estimated_score_gain", 0),
        reverse=True
    )
    
    # Add rank
    for i, rec in enumerate(recommendations, 1):
        rec["rank"] = i
    
    return recommendations


def estimate_score_improvement_timeline(
    profile: Dict[str, Any],
    recommendations: List[Dict[str, Any]],
    calculate_score_func
) -> List[Dict[str, Any]]:
    """
    Estimate how score improves over time as recommendations are implemented.
    
    Returns a week-by-week timeline assuming linear progress.
    
    Args:
        profile: Credit profile
        recommendations: List of recommendations from find_best_actions()
        calculate_score_func: Function to calculate score
        
    Returns:
        List of timeline entries with week and estimated score
    """
    
    try:
        current_score = calculate_score_func(profile)
    except Exception:
        current_score = 650
    
    if not recommendations:
        return [
            {"week": 0, "estimated_score": current_score, "action": "Current score"},
            {"week": 52, "estimated_score": current_score, "action": "No improvements planned"},
        ]
    
    # Calculate total potential gain
    total_gain = sum(r.get("estimated_score_gain", 0) for r in recommendations)
    
    if total_gain <= 0:
        return [
            {"week": 0, "estimated_score": current_score, "action": "Current score"},
        ]
    
    # Distribute gains over time (assume 2-3 month full effect, ramping up)
    # Week 0: current
    # Week 2: 10% of gains (reporting lag)
    # Week 4: 30% of gains
    # Week 8: 60% of gains
    # Week 16: 100% of gains (3-4 months)
    
    timeline = [
        {"week": 0, "estimated_score": current_score, "action": "Current score"},
        {
            "week": 2,
            "estimated_score": int(current_score + total_gain * 0.10),
            "action": "Early gains from credit mix changes"
        },
        {
            "week": 4,
            "estimated_score": int(current_score + total_gain * 0.30),
            "action": "First paydowns reflected"
        },
        {
            "week": 8,
            "estimated_score": int(current_score + total_gain * 0.60),
            "action": "Major improvements showing"
        },
        {
            "week": 16,
            "estimated_score": int(current_score + total_gain),
            "action": "Full effect of all recommendations"
        },
    ]
    
    return timeline


def get_quick_wins(
    recommendations: List[Dict[str, Any]],
    min_gain: float = 15
) -> List[Dict[str, Any]]:
    """
    Filter recommendations for quick wins (>15 points with low effort).
    
    Args:
        recommendations: Full recommendation list
        min_gain: Minimum score gain to consider a "quick win"
        
    Returns:
        Filtered list of quick wins
    """
    
    quick_wins = []
    
    for rec in recommendations:
        gain = rec.get("estimated_score_gain", 0)
        rec_type = rec.get("type")
        
        # Paydowns under $500 with >15 point gain are quick wins
        if rec_type == "paydown":
            amount = rec.get("paydown_amount", 0)
            if gain >= min_gain and amount <= 500:
                quick_wins.append(rec)
        
        # High-gain payoff recommendations
        elif rec_type == "payoff":
            if gain >= 25:  # Higher threshold for paying off
                quick_wins.append(rec)
    
    return quick_wins
