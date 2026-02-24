from sqlalchemy import Column, String, DateTime, Integer, Text
import uuid
from models.database import Base
from datetime import datetime

class ProfileSnapshot(Base):
    __tablename__ = "profile_snapshots"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String, index=True)
    snapshot_hash = Column(String)
    snapshot_json = Column(Text)
    score = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

def persist_profile_snapshot(profile: dict, metadata: dict = None):
    """
    Save a profile snapshot to the database.
    
    Args:
        profile: The credit profile dict
        metadata: Optional metadata about the snapshot
    
    Returns:
        The created ProfileSnapshot record or None on error
    """
    try:
        from models.database import SessionLocal
        import json
        
        db = SessionLocal()
        snapshot_json = json.dumps(profile)
        
        snapshot = ProfileSnapshot(
            id=uuid.uuid4(),
            profile_id=profile.get('id', 'unknown'),
            snapshot_json=snapshot_json,
            score=profile.get('score')
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot
    except Exception as e:
        print(f"Error persisting profile snapshot: {e}")
        return None