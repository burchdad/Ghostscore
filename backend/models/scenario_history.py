from sqlalchemy.orm import Session
from models.db_models import ScenarioHistory
from datetime import datetime
from typing import List, Dict, Any

def save_scenario_history(db: Session, profile_id: str, actions: List[Dict[str, Any]], original_score: int, simulated_score: int, actual_gain: int = None, timeline: List[Dict[str, Any]] = None, notes: str = None):
    entry = ScenarioHistory(
        profile_id=profile_id,
        actions=actions,
        original_score=original_score,
        simulated_score=simulated_score,
        actual_gain=actual_gain,
        timeline=timeline,
        notes=notes,
        created_at=datetime.utcnow()
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def get_scenario_history(db: Session, profile_id: str, limit: int = 100):
    return db.query(ScenarioHistory).filter_by(profile_id=profile_id).order_by(ScenarioHistory.created_at.desc()).limit(limit).all()
