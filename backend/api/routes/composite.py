from fastapi import APIRouter, HTTPException
from scoring.model_registry import ModelRegistry
from scoring.feature_engine import extract_features

router = APIRouter()

@router.post("/score/composite")
def score_composite(request: dict):
    try:
        profile = request.get("profile", {})
        features = extract_features(profile)
        scores = {}
        for model_name in ["fico8", "fico9", "fico10"]:
            model = ModelRegistry.get(model_name)
            scores[model_name] = model.score(features)
        composite = int(scores["fico8"] * 0.4 + scores["fico9"] * 0.3 + scores["fico10"] * 0.3)
        scores["composite"] = composite
        return scores
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
