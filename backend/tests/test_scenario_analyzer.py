import pytest
from scoring.scenario_analyzer import calculate_confidence_intervals, find_optimal_action_sequence, generate_action_priority_matrix
from scoring.fico_engine import FicoEngine

def test_calculate_confidence_intervals():
    engine = FicoEngine()
    profile = {
        'accounts': [
            {'id': 'card1', 'type': 'credit_card', 'name': 'Chase', 'balance': 2500, 'limit': 5000, 'open_date': '2020-01-15', 'status': 'active'},
        ],
        'derogatories': []
    }
    actions = [
        {'type': 'paydown', 'account_name': 'Chase', 'paydown_amount': 2050, 'estimated_gain': 35, 'priority': 'high'},
        {'type': 'payoff', 'account_name': 'Chase', 'paydown_amount': 450, 'estimated_gain': 18, 'priority': 'medium'},
    ]
    current_score = engine.calculate_score(profile)
    intervals = calculate_confidence_intervals(current_score, actions, engine.calculate_score)
    assert 'optimistic' in intervals
    assert 'realistic' in intervals
    assert 'conservative' in intervals
    assert intervals['optimistic']['score'] > current_score

def test_find_optimal_action_sequence_and_priority_matrix():
    engine = FicoEngine()
    profile = {
        'accounts': [
            {'id': 'card1', 'type': 'credit_card', 'name': 'Chase', 'balance': 2500, 'limit': 5000, 'open_date': '2020-01-15', 'status': 'active'},
        ],
        'derogatories': []
    }
    actions = [
        {'type': 'paydown', 'account_name': 'Chase', 'paydown_amount': 2050, 'estimated_gain': 35, 'priority': 'high'},
        {'type': 'payoff', 'account_name': 'Chase', 'paydown_amount': 450, 'estimated_gain': 18, 'priority': 'medium'},
    ]
    indices, gain, efficiency = find_optimal_action_sequence(profile, actions, engine.calculate_score)
    assert isinstance(indices, list)
    assert isinstance(gain, int)
    assert isinstance(efficiency, float)
    matrix = generate_action_priority_matrix(actions)
    assert 'quick_wins' in matrix
    assert 'strategic' in matrix
    assert isinstance(matrix['quick_wins'], list)
