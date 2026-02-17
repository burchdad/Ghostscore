import pytest
from scoring.optimizer import find_best_actions, estimate_score_improvement_timeline
from scoring.fico_engine import FicoEngine

def test_find_best_actions_paydown_and_payoff():
    profile = {
        'accounts': [
            {'id': 'card1', 'type': 'credit_card', 'name': 'Chase', 'balance': 2500, 'limit': 5000, 'open_date': '2020-01-15', 'status': 'active'},
            {'id': 'loan1', 'type': 'auto_loan', 'name': 'Car Loan', 'balance': 15000, 'limit': None, 'open_date': '2021-03-10', 'status': 'active'},
        ],
        'derogatories': []
    }
    engine = FicoEngine()
    actions = find_best_actions(profile, engine.calculate_score)
    # Should recommend a paydown for the credit card, not the loan
    paydown = [a for a in actions if a['type'] == 'paydown']
    payoff = [a for a in actions if a['type'] == 'payoff']
    assert any('Chase' in a['account_name'] for a in paydown)
    assert all(a['account_type'] == 'credit_card' for a in paydown)
    # Payoff only if gain > 20, so may or may not exist
    assert isinstance(actions, list)
    assert all('estimated_gain' in a for a in actions)

def test_estimate_score_improvement_timeline():
    profile = {
        'accounts': [
            {'id': 'card1', 'type': 'credit_card', 'name': 'Chase', 'balance': 2500, 'limit': 5000, 'open_date': '2020-01-15', 'status': 'active'},
        ],
        'derogatories': []
    }
    engine = FicoEngine()
    actions = find_best_actions(profile, engine.calculate_score)
    timeline = estimate_score_improvement_timeline(profile, actions, engine.calculate_score)
    assert isinstance(timeline, list)
    assert timeline[0]['milestone'] == 'Current score'
    assert all('score' in t for t in timeline)
