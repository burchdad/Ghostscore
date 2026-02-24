"""
Scenario Optimization Layer

Finds the best credit improvement actions for a user.
This is the core of GhostScore's advice engine.
"""

from typing import Dict, List, Any
from copy import deepcopy

from .feature_engine import extract_features
from .scorecards import determine_scorecard
from .action_sequence_ml import predict_optimal_sequence


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

    # === PAYDOWN RECOMMENDATIONS WITH UTILIZATION BINS ===
    utilization_bins = [0.88, 0.68, 0.48, 0.28, 0.08, 0.01]
    for account_idx, account in enumerate(accounts):
        account_type = account.get("account_type", account.get("type", "other"))
        if account_type != "credit_card":
            continue
        balance = float(account.get("balance", 0))
        credit_limit = account.get("credit_limit", account.get("limit", 1))
        limit = float(credit_limit) if credit_limit else 1
        if limit == 0:
            continue
        for bin_pct in utilization_bins:
            target_balance = round(limit * bin_pct, 2)
            if balance <= target_balance:
                continue
            paydown_amount = balance - target_balance
            simulated = deepcopy(profile)
            account_id = account.get("id")
            matched = False
            if account_id:
                for sim_acc in simulated.get("accounts", []):
                    if sim_acc.get("id") == account_id:
                        sim_acc["balance"] = target_balance
                        matched = True
                        break
            if not matched:
                if account_idx < len(simulated.get("accounts", [])):
                    simulated["accounts"][account_idx]["balance"] = target_balance
            try:
                new_score = calculate_score_func(simulated)
                gain = new_score - original_score
            except Exception:
                gain = 0
            if gain > 0:
                recommendations.append({
                    "type": "paydown",
                    "priority": "high" if gain > 30 else "medium" if gain > 15 else "low",
                    "account_id": account_id,
                    "account_name": account.get("issuer", account.get("name", "Unknown Account")),
                    "account_type": account_type,
                    "current_balance": balance,
                    "target_balance": target_balance,
                    "paydown_amount": paydown_amount,
                    "utilization_bin": bin_pct,
                    "estimated_gain": gain,
                    "description": f"Pay down {account.get('issuer', 'account')} to {int(bin_pct*100)}% utilization (${target_balance:.0f})",
                })

    # === CLOSE/PAY OFF RECOMMENDATIONS ===
    for account_idx, account in enumerate(accounts):
        account_type = account.get("account_type", account.get("type", "other"))
        if account_type not in ("credit_card", "personal_loan"):
            continue
        balance = float(account.get("balance", 0))
        if balance <= 0:
            continue
        simulated = deepcopy(profile)
        account_id = account.get("id")
        matched = False
        if account_id:
            for sim_acc in simulated.get("accounts", []):
                if sim_acc.get("id") == account_id:
                    sim_acc["balance"] = 0
                    matched = True
                    break
        if not matched:
            if account_idx < len(simulated.get("accounts", [])):
                simulated["accounts"][account_idx]["balance"] = 0
        try:
            new_score = calculate_score_func(simulated)
            gain = new_score - original_score
        except Exception:
            gain = 0
        if gain > 20:
            recommendations.append({
                "type": "payoff",
                "priority": "high" if gain > 40 else "medium" if gain > 20 else "low",
                "account_id": account_id,
                "account_name": account.get("issuer", account.get("name", "Unknown Account")),
                "account_type": account_type,
                "current_balance": balance,
                "target_balance": 0,
                "paydown_amount": balance,
                "estimated_gain": gain,
                "description": f"Pay off {account.get('issuer', 'account')} completely (${balance:.0f})",
            })

    # === DEROGATORY REMOVAL (if applicable) ===
    derogatories = profile.get("derogatories", [])
    if derogatories:
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
                "estimated_gain": gain,
                "note": "Derogatory marks can be disputed or may age out.",
            })

    # ML-BASED ACTION SEQUENCING (if model available)
    try:
        features = extract_features(profile)
        # Only use ML if there are enough recommendations to sequence
        if len(recommendations) > 1:
            seq_indices = predict_optimal_sequence(features, max_len=len(recommendations))
            # Defensive: filter out-of-bounds indices
            seq_indices = [i for i in seq_indices if 0 <= i < len(recommendations)]
            # Reorder recommendations by ML-predicted sequence
            recommendations = [recommendations[i] for i in seq_indices]
    except Exception:
        # Fallback: sort by score gain (descending)
        recommendations.sort(key=lambda x: x.get("estimated_gain", 0), reverse=True)

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
            {"week": 0, "score": current_score, "milestone": "Current score"},
            {"week": 52, "score": current_score, "milestone": "No improvements planned"},
        ]
    
    # Integrate TimelineEngine for realistic score projection
    from .timeline_engine import TimelineEngine, TimelineEvent
    timeline_engine = TimelineEngine()
    timeline_events = []
    for rec in recommendations:
        action_type = rec.get("type")
        score_delta = rec.get("estimated_gain", 0)
        # Use realistic delays/ramp from TimelineEngine.ACTION_DELAYS
        delay, ramp = timeline_engine.ACTION_DELAYS.get(action_type, (2, 6))
        timeline_events.append(
            TimelineEvent(
                action_type=action_type,
                score_delta=score_delta,
                delay_weeks=delay,
                ramp_weeks=ramp
            )
        )
    timeline_scores = timeline_engine.build_timeline(current_score, timeline_events, total_weeks=16)
    timeline = [
        {"week": i, "score": score, "milestone": "Projected"} for i, score in enumerate(timeline_scores)
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
        gain = rec.get("estimated_gain", 0)
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
