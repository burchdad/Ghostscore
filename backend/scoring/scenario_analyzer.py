"""
Scenario Analysis Engine

Supports:
- Multi-action scenario simulation
- Confidence intervals (optimistic/realistic/conservative)
- Action sequencing optimization
- Custom parameter exploration
"""

from typing import Dict, List, Any, Tuple
from copy import deepcopy
import math


def calculate_confidence_intervals(
    current_score: int,
    recommended_actions: List[Dict[str, Any]],
    calculate_score_func
) -> Dict[str, Dict[str, int]]:
    """
    Calculate optimistic, realistic, and conservative score projections.
    
    Assumptions:
    - Realistic: 70% of maximum potential gain
    - Optimistic: 100% of maximum potential gain (all recommendations implemented perfectly)
    - Conservative: 40% of maximum potential gain (partial/delayed implementation)
    
    Args:
        current_score: Current FICO score
        recommended_actions: List of recommended actions with estimated_gain
        calculate_score_func: Function to calculate score
        
    Returns:
        Dict with optimistic, realistic, conservative scores and details
    """
    
    total_max_gain = sum(a.get('estimated_gain', 0) for a in recommended_actions)
    
    scenarios = {
        'optimistic': {
            'score': current_score + total_max_gain,
            'gain': total_max_gain,
            'description': 'All recommendations implemented perfectly within 4-6 weeks',
            'confidence': 0.6,
        },
        'realistic': {
            'score': int(current_score + (total_max_gain * 0.7)),
            'gain': int(total_max_gain * 0.7),
            'description': 'Most recommendations implemented within 8-12 weeks',
            'confidence': 0.8,
        },
        'conservative': {
            'score': int(current_score + (total_max_gain * 0.4)),
            'gain': int(total_max_gain * 0.4),
            'description': 'Some actions delayed, partial implementation',
            'confidence': 0.65,
        },
    }
    
    return scenarios


def simulate_multi_action(
    profile: Dict[str, Any],
    action_indices: List[int],
    recommended_actions: List[Dict[str, Any]],
    calculate_score_func
) -> Dict[str, Any]:
    """
    Simulate multiple actions applied simultaneously.
    
    Args:
        profile: Credit profile
        action_indices: List of action indices to apply
        recommended_actions: All available recommendations
        calculate_score_func: Function to calculate score
        
    Returns:
        Result dict with simulated score, individual gains, total gain, timeline
    """
    
    if not action_indices:
        return {
            'current_score': calculate_score_func(profile),
            'simulated_score': calculate_score_func(profile),
            'actions_applied': [],
            'total_gain': 0,
        }
    
    # Start with current score
    original_score = calculate_score_func(profile)
    
    # Apply all actions to a copy of the profile
    simulated_profile = deepcopy(profile)
    applied_actions = []
    total_gain = 0
    
    for idx in action_indices:
        if idx >= len(recommended_actions):
            continue
        
        action = recommended_actions[idx]
        action_type = action.get('type')
        
        # Apply action to simulated profile
        if action_type == 'paydown':
            account_name = action.get('account_name')
            target_balance = action.get('target_balance', 0)
            
            for acc in simulated_profile.get('accounts', []):
                if acc.get('issuer') == account_name or acc.get('name') == account_name:
                    acc['balance'] = target_balance
                    break
        
        elif action_type == 'payoff':
            account_name = action.get('account_name')
            
            for acc in simulated_profile.get('accounts', []):
                if acc.get('issuer') == account_name or acc.get('name') == account_name:
                    acc['balance'] = 0
                    break
        
        elif action_type == 'derogatory_removal':
            simulated_profile['derogatories'] = []
        
        applied_actions.append({
            'action': action,
            'type': action_type,
            'estimated_gain': action.get('estimated_gain', 0),
        })
        total_gain += action.get('estimated_gain', 0)
    
    # Calculate new score with all actions applied
    simulated_score = calculate_score_func(simulated_profile)
    
    # Calculate actual gain (may differ from estimated due to interactions)
    actual_gain = simulated_score - original_score
    
    return {
        'original_score': original_score,
        'simulated_score': simulated_score,
        'actions_applied': applied_actions,
        'total_estimated_gain': total_gain,
        'actual_gain': actual_gain,
        'action_count': len(applied_actions),
        'timeline': _estimate_action_timeline(applied_actions, actual_gain, original_score),
    }


def _estimate_action_timeline(
    applied_actions: List[Dict[str, Any]],
    actual_gain: int,
    original_score: int
) -> List[Dict[str, Any]]:
    """
    Estimate week-by-week timeline for multiple actions.
    
    Assumes:
    - Week 0: Current score
    - Week 2: 15% of gains (quick initial response)
    - Week 4: 40% of gains (first reports)
    - Week 8: 70% of gains (most changes reflected)
    - Week 16: 100% of gains (full effect)
    """
    
    # Integrate TimelineEngine for realistic score projection
    from .timeline_engine import TimelineEngine, TimelineEvent
    timeline_engine = TimelineEngine()
    timeline_events = []
    for action in applied_actions:
        action_type = action.get('type')
        score_delta = action.get('estimated_gain', 0)
        delay, ramp = timeline_engine.ACTION_DELAYS.get(action_type, (2, 6))
        timeline_events.append(
            TimelineEvent(
                action_type=action_type,
                score_delta=score_delta,
                delay_weeks=delay,
                ramp_weeks=ramp
            )
        )
    timeline_scores = timeline_engine.build_timeline(original_score, timeline_events, total_weeks=16)
    timeline = [
        {'week': i, 'score': score, 'milestone': 'Projected'} for i, score in enumerate(timeline_scores)
    ]
    return timeline


def find_optimal_action_sequence(
    profile: Dict[str, Any],
    recommended_actions: List[Dict[str, Any]],
    calculate_score_func,
    max_cost: float = None
) -> Tuple[List[int], int, float]:
    """
    Find the optimal sequence of actions to maximize score gain per unit cost.
    
    Uses a greedy algorithm to rank actions by gain/effort ratio.
    
    Args:
        profile: Credit profile
        recommended_actions: All recommendations
        calculate_score_func: Score calculation function
        max_cost: Total budget constraint (sum of paydown_amount values)
        
    Returns:
        Tuple of (action_indices, expected_gain, efficiency_score)
    """
    
    if not recommended_actions:
        return [], 0, 0.0
    
    # Calculate efficiency score for each action
    action_scores = []
    for idx, action in enumerate(recommended_actions):
        gain = action.get('estimated_gain', 0)
        
        # Estimate effort/cost
        effort = 0
        if action.get('type') == 'paydown':
            effort = action.get('paydown_amount', 0)
        elif action.get('type') == 'payoff':
            effort = action.get('paydown_amount', 0)
        
        # Calculate efficiency: gain per unit effort
        efficiency = gain / (effort + 1) if effort >= 0 else 0
        
        action_scores.append({
            'index': idx,
            'action': action,
            'gain': gain,
            'effort': effort,
            'efficiency': efficiency,
            'priority': action.get('priority', 'medium'),
        })
    
    # Sort by efficiency (descending)
    action_scores.sort(key=lambda x: x['efficiency'], reverse=True)
    
    # Select actions up to budget constraint
    selected_indices = []
    total_cost = 0
    total_gain = 0
    total_efficiency = 0
    
    for scored_action in action_scores:
        if max_cost and total_cost + scored_action['effort'] > max_cost:
            continue
        
        selected_indices.append(scored_action['index'])
        total_cost += scored_action['effort']
        total_gain += scored_action['gain']
        total_efficiency += scored_action['efficiency']
    
    return selected_indices, total_gain, total_efficiency


def generate_action_priority_matrix(
    recommended_actions: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group actions into priority matrix (effort vs impact).
    
    Returns quadrants:
    - Quick wins: High impact, low effort
    - Strategic: High impact, high effort
    - Fill-ins: Low impact, low effort
    - Avoid: Low impact, high effort
    """
    
    if not recommended_actions:
        return {
            'quick_wins': [],
            'strategic': [],
            'fill_ins': [],
            'avoid': [],
        }
    
    # Calculate median effort
    efforts = []
    for action in recommended_actions:
        if action.get('type') == 'paydown':
            efforts.append(action.get('paydown_amount', 0))
        elif action.get('type') == 'payoff':
            efforts.append(action.get('paydown_amount', 0))
    
    median_effort = sum(efforts) / len(efforts) if efforts else 0
    median_gain = sum(a.get('estimated_gain', 0) for a in recommended_actions) / len(recommended_actions)
    
    matrix = {
        'quick_wins': [],
        'strategic': [],
        'fill_ins': [],
        'avoid': [],
    }
    
    for action in recommended_actions:
        gain = action.get('estimated_gain', 0)
        
        if action.get('type') == 'paydown':
            effort = action.get('paydown_amount', 0)
        elif action.get('type') == 'payoff':
            effort = action.get('paydown_amount', 0)
        else:
            effort = 0  # Derogatory removal has no effort cost
        
        high_impact = gain >= median_gain
        low_effort = effort <= median_effort
        
        if high_impact and low_effort:
            matrix['quick_wins'].append(action)
        elif high_impact and not low_effort:
            matrix['strategic'].append(action)
        elif not high_impact and low_effort:
            matrix['fill_ins'].append(action)
        else:
            matrix['avoid'].append(action)
    
    return matrix
