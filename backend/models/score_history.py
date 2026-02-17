from sqlalchemy.orm import Session
from models.db_models import ScoreHistory
from datetime import datetime

def save_score_history(db: Session, profile_id: str, score: int, payment_history: int = None, utilization: int = None, age: int = None, new_credit: int = None, mix: int = None):
    entry = ScoreHistory(
        profile_id=profile_id,
        score=score,
        payment_history=payment_history,
        utilization=utilization,
        age=age,
        new_credit=new_credit,
        mix=mix,
        created_at=datetime.utcnow()
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def get_score_history(db: Session, profile_id: str, limit: int = 100):
    return db.query(ScoreHistory).filter_by(profile_id=profile_id).order_by(ScoreHistory.created_at.desc()).limit(limit).all()
