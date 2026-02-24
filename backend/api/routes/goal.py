from fastapi import APIRouter, HTTPException
from typing import Any, Dict
from scoring.goal_solver import GoalSolver, GoalRequest, GoalPreferences
from scoring.fico_engine import FicoEngine
from scoring.optimizer import find_best_actions
from scoring.scenario_analyzer import simulate_multi_action
from scoring.timeline_engine import TimelineEngine

router = APIRouter()

@router.post("/optimize/goal")
def optimize_goal_route(request: Dict[str, Any]):
    try:
        import random
        deterministic = request.get("deterministic", False)
        if deterministic:
            random.seed(42)
            try:
                import numpy as np
                np.random.seed(42)
            except ImportError:
                pass
        profile = request.get("profile", {})
        target_score = request.get("target_score", 700)
        budget = request.get("budget", 2000)
        timeline_weeks = request.get("timeline_weeks", 16)
        risk_tolerance = request.get("risk_tolerance", "medium")
        preferences_dict = request.get("preferences", {})
        preferences = GoalPreferences(
            avoid_new_accounts=preferences_dict.get("avoid_new_accounts", True),
            avoid_hard_inquiries=preferences_dict.get("avoid_hard_inquiries", True),
            prefer_paydown_over_settlement=preferences_dict.get("prefer_paydown_over_settlement", True)
        )
        goal_req = GoalRequest(
            target_score=target_score,
            budget=budget,
            timeline_weeks=timeline_weeks,
            risk_tolerance=risk_tolerance,
            preferences=preferences
        )
        # Instantiate engines
        engine = FicoEngine()
        optimizer = type('Optimizer', (), {"get_actions": staticmethod(lambda p: find_best_actions(p, engine.calculate_score))})()
        scenario_analyzer = type('ScenarioAnalyzer', (), {"run": staticmethod(lambda p, plan: simulate_multi_action(p, [i for i, _ in enumerate(plan)], plan, engine.calculate_score))})()
        timeline_engine = TimelineEngine()
        goal_solver = GoalSolver(engine, optimizer, scenario_analyzer, timeline_engine)
        result = goal_solver.solve(profile, goal_req)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
