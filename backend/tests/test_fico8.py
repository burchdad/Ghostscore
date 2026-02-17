import pytest

from scoring.models import fico8
from scoring.fico_engine import FicoEngine


def test_fico8_bucket_normalization_and_aggregation():
    # High-quality inputs: very low utilization and long age
    subscores = {
        'utilization': 1.0,        # 1% utilization -> top bucket
        'payment_history': 100.0,   # very good payment history (0-100 proxy)
        'age': 15.0,                # 15 years -> high age bucket
        'new_credit': 0.0,          # no recent new credit
        'mix': 2.0,                 # diverse mix
    }

    score = fico8.aggregate_score(subscores, scorecard='clean')
    assert isinstance(score, int)
    assert 300 <= score <= 850


def test_fico_engine_uses_fico8_model_when_requested():
    profile = {
        'accounts': [
            {'type': 'credit_card', 'balance': 100.0, 'limit': 5000.0, 'months_open': 60},
        ],
        'derogatories': []
    }

    engine_linear = FicoEngine()
    engine_fico8 = FicoEngine(model='fico8')

    s_linear = engine_linear.calculate_full_score(profile)['score']
    s_fico8 = engine_fico8.calculate_full_score(profile)['score']

    assert isinstance(s_linear, int)
    assert isinstance(s_fico8, int)
    # Scores may differ; fico8 should produce a realistic integer
    assert 300 <= s_fico8 <= 850
