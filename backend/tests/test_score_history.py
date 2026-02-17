import pytest
from fastapi.testclient import TestClient
from backend.main import app
from models.database import SessionLocal
from models.db_models import CreditProfile, User

def create_test_profile(db):
    user = User(email="testuser@example.com", password="testpass")
    db.add(user)
    db.commit()
    db.refresh(user)
    profile = CreditProfile(user_id=user.id, name="Test Profile")
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return user, profile

def test_score_history_endpoints():
    client = TestClient(app)
    db = SessionLocal()
    user, profile = create_test_profile(db)
    # Save a score snapshot
    resp = client.post(f"/profiles/{profile.id}/score_history", json={
        "score": 700,
        "payment_history": 90,
        "utilization": 20,
        "age": 60,
        "new_credit": 80,
        "mix": 70
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["score"] == 700
    # Retrieve score history
    resp2 = client.get(f"/profiles/{profile.id}/score_history")
    assert resp2.status_code == 200, resp2.text
    history = resp2.json()
    assert isinstance(history, list)
    assert any(entry["score"] == 700 for entry in history)
    db.close()
