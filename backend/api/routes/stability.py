from fastapi import APIRouter, HTTPException
from scoring.fico_engine import FicoEngine
from backend.models.profile_scores import ProfileScore
from backend.models.database import SessionLocal

router = APIRouter()

@router.get("/score/stability/{profile_id}")
def get_score_stability(profile_id: str):
    try:
        session = SessionLocal()
        history = session.query(ProfileScore).filter_by(profile_id=profile_id).order_by(ProfileScore.created_at.desc()).all()
        score_history = [{"score": s.score, "created_at": s.created_at} for s in history]
        engine = FicoEngine()
        stability = engine.compute_stability_index(score_history)
        return {"profile_id": profile_id, "stability_index": stability, "history": score_history}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
