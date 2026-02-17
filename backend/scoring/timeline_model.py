"""
Timeline Model for GhostScore

Simulates realistic reporting delays for credit actions.
"""
from typing import List, Dict, Any
import random

def estimate_reporting_delay(action_type: str) -> int:
    """
    Estimate reporting delay in days for a given action type.
    """
    if action_type == "paydown":
        return random.randint(15, 45)
    elif action_type == "utilization":
        return random.randint(25, 35)
    elif action_type == "derogatory_removal":
        return random.randint(30, 90)
    elif action_type == "inquiry_aging":
        return random.randint(180, 365)
    return 30

def apply_timeline_model(actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Annotate actions with expected reporting delays.
    """
    timeline = []
    current_day = 0
    for action in actions:
        delay = estimate_reporting_delay(action.get("type", "other"))
        current_day += delay
        timeline.append({**action, "expected_day": current_day})
    return timeline
