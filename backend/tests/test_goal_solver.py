import pytest
from scoring.goal_solver import GoalSolver, GoalRequest, GoalPreferences
from scoring.fico_engine import FicoEngine
from scoring.optimizer import find_best_actions
from scoring.scenario_analyzer import simulate_multi_action
from scoring.timeline_engine import TimelineEngine

@pytest.fixture
def engines():
    engine = FicoEngine()
    optimizer = type('Optimizer', (), {"get_actions": staticmethod(lambda p: find_best_actions(p, engine.calculate_score))})()
    scenario_analyzer = type('ScenarioAnalyzer', (), {"run": staticmethod(lambda p, plan: simulate_multi_action(p, [i for i, _ in enumerate(plan)], plan, engine.calculate_score))})()
    timeline_engine = TimelineEngine()
    return engine, optimizer, scenario_analyzer, timeline_engine


def test_goal_solver_returns_plan_under_budget(engines):
    engine, optimizer, scenario_analyzer, timeline_engine = engines
    profile = {"accounts": [{"account_type": "credit_card", "balance": 1500, "credit_limit": 3000, "issuer": "card1"}], "derogatories": []}
    req = GoalRequest(target_score=700, budget=2000, timeline_weeks=16)
    goal_solver = GoalSolver(engine, optimizer, scenario_analyzer, timeline_engine)
    result = goal_solver.solve(profile, req)
    assert result["best_plan"]["budget_used"] <= req.budget


def test_goal_solver_timeline_length(engines):
    engine, optimizer, scenario_analyzer, timeline_engine = engines
    profile = {"accounts": [{"account_type": "credit_card", "balance": 1500, "credit_limit": 3000, "issuer": "card1"}], "derogatories": []}
    req = GoalRequest(target_score=700, budget=2000, timeline_weeks=12)
    goal_solver = GoalSolver(engine, optimizer, scenario_analyzer, timeline_engine)
    result = goal_solver.solve(profile, req)
    assert len(result["best_plan"]["timeline"]) == req.timeline_weeks


def test_goal_solver_preferences_filter_actions(engines):
    engine, optimizer, scenario_analyzer, timeline_engine = engines
    profile = {"accounts": [{"account_type": "credit_card", "balance": 1500, "credit_limit": 3000, "issuer": "card1"}], "derogatories": []}
    req = GoalRequest(target_score=700, budget=2000, timeline_weeks=16, preferences=GoalPreferences(avoid_new_accounts=True))
    goal_solver = GoalSolver(engine, optimizer, scenario_analyzer, timeline_engine)
    result = goal_solver.solve(profile, req)
    for action in result["best_plan"]["actions"]:
        assert action["type"] != "new_account"
