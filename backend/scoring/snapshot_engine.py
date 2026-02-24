import json
from datetime import datetime
from models.database import SessionLocal

import hashlib

class SnapshotEngine:
    def save_snapshot(self, profile_id: str, profile: dict, score: int):
        from models import profile_snapshots
        session = SessionLocal()
        profile_json = json.dumps(profile, sort_keys=True)
        snapshot_hash = hashlib.sha256(profile_json.encode()).hexdigest()
        snapshot = profile_snapshots.ProfileSnapshot(
            profile_id=profile_id,
            snapshot_hash=snapshot_hash,
            snapshot_json=profile_json,
            score=score,
            created_at=datetime.utcnow()
        )
        session.add(snapshot)
        session.commit()
        session.close()
