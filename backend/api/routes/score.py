from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict
from scoring.model_registry import ModelRegistry
from scoring.feature_engine import extract_features

router = APIRouter()

@router.post("/score/all")
def score_all_models(request: Dict[str, Any]):
    try:
        profile = request.get("profile", {})
        features = extract_features(profile)
        results = {}
        for model_name in ["fico8", "fico9", "fico10"]:
            model = ModelRegistry.get(model_name)
            results[model_name] = model.score(features)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
