from sqlalchemy import Column, String, Integer, Float, DateTime
from models.database import Base
from datetime import datetime
import uuid

class ProfileScore(Base):
    __tablename__ = "profile_scores"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String, index=True, nullable=False)
    model = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    calibrated_score = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

def persist_profile_score(profile: dict, model: str, score: float, version: str = None, score_hash: str = None):
    """
    Save a score to the database.
    
    Args:
        profile: The credit profile dict
        model: Model name (fico8, fico9, fico10, composite)
        score: The calculated score
        version: Model version  
        score_hash: Hash of score for integrity checking
    
    Returns:
        The created ProfileScore record
    """
    try:
        from models.database import SessionLocal
        db = SessionLocal()
        
        profile_score = ProfileScore(
            id=str(uuid.uuid4()),
            profile_id=profile.get('id', 'unknown'),
            model=model,
            score=int(score)
        )
        db.add(profile_score)
        db.commit()
        db.refresh(profile_score)
        return profile_score
    except Exception as e:
        print(f"Error persisting profile score: {e}")
        return None