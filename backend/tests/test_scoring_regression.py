import pytest
from backend.scoring.fico_engine import FicoEngine
import json

@pytest.fixture
def scorer():
    return FicoEngine()

def load_fixture(name):
    with open(f"backend/tests/fixtures/{name}", "r") as f:
        return json.load(f)

def test_known_profile_1(scorer):
    profile = load_fixture("profile_1.json")
    score = scorer.calculate_score(profile)
    assert score == 712

def test_known_profile_2(scorer):
    profile = load_fixture("profile_2.json")
    score = scorer.calculate_score(profile)
    assert score == 685

def test_known_profile_3(scorer):
    profile = load_fixture("profile_3.json")
    score = scorer.calculate_score(profile)
    assert score == 730

def test_known_profile_4(scorer):
    profile = load_fixture("profile_4.json")
    score = scorer.calculate_score(profile)
    assert score == 660

def test_known_profile_5(scorer):
    profile = load_fixture("profile_5.json")
    score = scorer.calculate_score(profile)
    assert score == 701
