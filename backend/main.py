from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, Query, Body, Response, Path, Request
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import re
from models.database import get_db, init_db, SessionLocal
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GhostScore API", version="0.1.0")

# Enable CORS with explicit configuration BEFORE any routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Catch-all OPTIONS handler for CORS preflight - must return 200
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return ""

# ============= Models =============

class Account(BaseModel):
    id: Optional[str] = None
    type: str  # "credit_card", "loan", "mortgage", etc.
    name: str
    balance: float
    limit: Optional[float] = None
    open_date: date
    status: str = "active"  # active, closed, charged_off


class Derogatory(BaseModel):
    id: Optional[str] = None
    type: str  # "late_payment", "collection", "charge_off", "bankruptcy" etc.
    date: date
    details: Optional[str] = None


class CreditProfile(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    accounts: List[Account]
    derogatories: List[Derogatory] = []


class ScoreResponse(BaseModel):
    score: int
    payment_history: int
    utilization: int
    age: int
    new_credit: int
    mix: int


class ScenarioRequest(BaseModel):
    profile: CreditProfile
    account_id: str
    new_balance: float


class RecommendationResponse(BaseModel):
    actions: List[dict]
    estimated_score_gain: int


class CreateProfileRequest(BaseModel):
    email: str
    profile_name: str = "My Profile"


class ProfileResponse(BaseModel):
    id: str
    name: str
    
    class Config:
        from_attributes = True


class ExtractedAccount(BaseModel):
    """Account extracted from credit report"""
    name: str
    type: str
    balance: float
    limit: Optional[float] = None
    open_date: str
    status: str = "active"


class CreditReportUploadResponse(BaseModel):
    """Response from credit report upload"""
    status: str
    accounts: List[ExtractedAccount]
    message: Optional[str] = None


class ImportAccountsRequest(BaseModel):
    """Request to import accounts from upload"""
    accounts: List[ExtractedAccount]
    selected_indices: Optional[List[int]] = None


class ScoreHistoryEntry(BaseModel):
    id: Optional[str] = None
    profile_id: str
    score: int
    payment_history: Optional[int] = None
    utilization: Optional[int] = None
    age: Optional[int] = None
    new_credit: Optional[int] = None
    mix: Optional[int] = None
    created_at: Optional[str] = None


class ScenarioHistoryEntry(BaseModel):
    id: Optional[str] = None
    profile_id: str
    actions: List[dict]
    original_score: int
    simulated_score: int
    actual_gain: Optional[int] = None
    timeline: Optional[List[dict]] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    pinned: Optional[bool] = False
    feedback: Optional[str] = None
    created_at: Optional[str] = None


# ============= Credit Velocity Metric Endpoint =============
from models.database import SessionLocal
from models.profile_snapshots import ProfileSnapshot
@app.get("/score/velocity/{profile_id}")
def score_velocity(profile_id: str):
    session = SessionLocal()
    # Get last 6 snapshots (assume weekly)
    history = session.query(ProfileSnapshot).filter_by(profile_id=profile_id).order_by(ProfileSnapshot.created_at.desc()).limit(6).all()
    if len(history) < 2:
        return {"velocity": 0, "trend": "stable", "projected_30_day_gain": 0}
    scores = [s.score for s in reversed(history)]
    weeks = len(scores) - 1
    velocity = (scores[-1] - scores[0]) / weeks if weeks else 0
    trend = "improving" if velocity > 0 else "declining" if velocity < 0 else "stable"
    projected_30 = int(velocity * 4)
    return {"velocity": round(velocity, 2), "trend": trend, "projected_30_day_gain": projected_30}
# ============= Score Consistency Validator Endpoint =============
from fastapi import Request
from scoring.stability_index import ScoreStabilityIndex
import numpy as np

@app.post("/score/validate")
async def validate_score(request: Request):
    data = await request.json()
    profile = data.get("profile", {})
    # Profile completeness
    required_fields = ["accounts", "derogatories"]
    consistent = all(field in profile for field in required_fields)
    # Utilization stability
    utils = [a.get("balance", 0)/a.get("credit_limit", 1) for a in profile.get("accounts", []) if a.get("credit_limit")]
    util_stability = float(np.std(utils)) if utils else 0.0
    # Account age stability
    ages = [a.get("open_date") for a in profile.get("accounts", []) if a.get("open_date")]
    age_stability = 1.0 if len(set(ages)) > 1 else 0.0
    # Derogatory volatility
    derog_types = [d.get("type") for d in profile.get("derogatories", [])]
    derog_volatility = float(len(set(derog_types))) / (len(derog_types) or 1)
    # Stability index
    stability_index = ScoreStabilityIndex().compute(utils) if utils else 0.0
    # Confidence (simple heuristic)
    confidence = float(1.0 - (util_stability + age_stability + derog_volatility)/3)
    return {
        "consistent": consistent,
        "stability_index": round(stability_index, 3),
        "confidence": round(confidence, 3)
    }
# === Imports for new endpoints and persistence ===
from scoring.score_forecast_ml import ml_score_forecaster
from fastapi import FastAPI, HTTPException
from scoring.model_registry import ModelRegistry
from scoring.calibration_engine import CalibrationEngine
from scoring.timeline_engine import TimelineEngine
from scoring.goal_solver import GoalSolver
from scoring.aggregator import CompositeScorer
from scoring.stability_index import ScoreStabilityIndex
from models.profile_scores import persist_profile_score
from models.profile_snapshots import persist_profile_snapshot
from models.calibration import ProfileCalibration
from models.database import SessionLocal
import hashlib
# ============= Predictive Score Forecasting Endpoint =============

class ScoreForecastRequest(BaseModel):
    profile: CreditProfile
    weeks: int = 16

@app.post("/score/forecast")
def forecast_score(request: ScoreForecastRequest):
    """
    Predict week-by-week credit score trajectory using ML regression model.
    Returns a list of predicted scores for each week.
    """
    try:
        from scoring.feature_engine import extract_features
        features = extract_features(request.profile.dict() if hasattr(request.profile, 'dict') else request.profile)
        forecast = ml_score_forecaster.predict(features, weeks=request.weeks)
        return {"forecast": forecast, "weeks": request.weeks}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============= Multi-Model Score Endpoint =============
class MultiModelScoreRequest(BaseModel):
    profile: dict
    models: list[str] = ["fico8", "fico9", "fico10", "linear"]



# ============= Composite Score Endpoint =============
@app.post("/score/composite")
def composite_score(profile: CreditProfile):
    """
    Return composite score (average) across multiple models.
    """
    try:
        models = ["fico8", "fico9", "fico10"]
        engine = fico_engine
        scores = []
        for model_name in models:
            result = engine.calculate_full_score(profile)
            scores.append(result.get('score', 0))
        # Simple average
        composite = sum(scores) / len(scores) if scores else 0
        return {"composite": int(composite)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============= Score Stability Index Endpoint =============
@app.post("/score/stability")
def score_stability(profile: CreditProfile):
    """
    Return score stability index.
    """
    try:
        if not profile.accounts or len(profile.accounts) == 0:
            return {"stability_index": 0, "risk_level": "unknown"}
        
        # Calculate stability based on account diversity and payment history
        utilization_variance = 0
        if len(profile.accounts) > 1:
            utilizations = []
            for acc in profile.accounts:
                if acc.limit and acc.limit > 0:
                    utilizations.append(acc.balance / acc.limit)
                else:
                    utilizations.append(acc.balance / 1000)  # default limit
            
            avg = sum(utilizations) / len(utilizations)
            variance = sum((u - avg) ** 2 for u in utilizations) / len(utilizations)
            utilization_variance = variance
        
        # Account age diversity (binary: have varied account ages or not)
        account_ages = len(set(acc.open_date.year for acc in profile.accounts))
        age_diversity = min(account_ages / 3, 1.0)  # normalize to 0-1
        
        # Derogatory volatility
        derogatory_factor = 1.0 - (len(profile.derogatories) / 10.0) if profile.derogatories else 1.0
        derogatory_factor = max(0, derogatory_factor)
        
        # Composite stability (0-100)
        stability_index = int(((1 - utilization_variance) * 0.4 + age_diversity * 0.3 + derogatory_factor * 0.3) * 100)
        stability_index = max(0, min(100, stability_index))
        
        risk_level = "low" if stability_index > 70 else "medium" if stability_index > 40 else "high"
        
        return {"stability_index": stability_index, "risk_level": risk_level}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============= Score All Models Endpoint =============
@app.post("/score/all")
def score_all_models(profile: CreditProfile):
    """
    Return scores from multiple models.
    """
    try:
        engine = fico_engine
        result = engine.calculate_full_score(profile)
        score = result.get('score', 0)
        
        # Return same score for all models (simplified for now)
        return {
            "fico8": int(score),
            "fico9": int(score * 0.98),  # slight variation
            "fico10": int(score * 1.02),  # slight variation
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============= Strategy Optimization Endpoint =============
class OptimizeGoalRequest(BaseModel):
    profile: dict
    target_score: int
    budget: Optional[float] = None
    timeline_weeks: Optional[int] = None

@app.post("/optimize/goal")
def optimize_goal(request: OptimizeGoalRequest):
    """
    Compute optimal strategy sequence to reach a target score under budget/timeline constraints.
    Returns optimal actions, expected timeline, and probability of success (placeholder).
    """
    profile = request.profile
    target_score = request.target_score
    budget = request.budget
    timeline_weeks = request.timeline_weeks

    # Use existing optimizer logic (find_best_actions, estimate_score_improvement_timeline)
    actions = find_best_actions(profile, fico_engine.calculate_score)
    timeline = estimate_score_improvement_timeline(profile, actions, fico_engine.calculate_score)

    # Filter actions to fit constraints (simple greedy for now)
    selected_actions = []
    total_cost = 0
    for action in actions:
        if budget is not None and 'cost' in action and (total_cost + action['cost'] > budget):
            continue
        selected_actions.append(action)
        total_cost += action.get('cost', 0)
        # Stop if target score is reached in timeline
        if 'estimated_gain' in action and sum(a.get('estimated_gain', 0) for a in selected_actions) + timeline[0]['score'] >= target_score:
            break

    expected_score = timeline[0]['score'] + sum(a.get('estimated_gain', 0) for a in selected_actions)
    expected_timeline = timeline[:len(selected_actions)+1] if timeline_weeks is None else [t for t in timeline if t['week'] <= timeline_weeks]

    # Placeholder for probability of success
    probability_of_success = 0.95 if expected_score >= target_score else 0.5

    return {
        "optimal_strategy_sequence": selected_actions,
        "expected_score_timeline": expected_timeline,
        "probability_of_success": probability_of_success,
        "final_expected_score": expected_score,
        "target_score": target_score,
        "budget_used": total_cost,
    }
from scoring.calibration_engine import CalibrationEngine
# ============= Calibration Endpoints =============

from pydantic import BaseModel
from models.database import SessionLocal

class CalibrationRequest(BaseModel):
    estimated_score: float
    actual_score: float

@app.post("/profiles/{profile_id}/calibrate")
def calibrate_profile(profile_id: str, req: CalibrationRequest):
    """Submit actual score for a profile to calibrate future estimates."""
    db = SessionLocal
    calibration_engine = CalibrationEngine(db)
    # Store offset and scale based on actual vs estimated
    session = db()
    from models.calibration import ProfileCalibration
    calibration = session.query(ProfileCalibration).filter_by(profile_id=profile_id).first()
    offset = req.actual_score - req.estimated_score
    scale = 1.0
    if calibration:
        calibration.offset = offset
        calibration.scale = scale
    else:
        calibration = ProfileCalibration(profile_id=profile_id, offset=offset, scale=scale)
        session.add(calibration)
    session.commit()
    return {"profile_id": profile_id, "correction": offset}

@app.get("/profiles/{profile_id}/calibrated-score")
def get_calibrated_score(profile_id: str, estimated_score: float):
    """Get a calibrated score estimate for a profile."""
    db = SessionLocal
    calibration_engine = CalibrationEngine(db)
    corrected = calibration_engine.apply_calibration(profile_id, estimated_score)
    return {"profile_id": profile_id, "calibrated_score": corrected}
# ============= Scenario Feedback Endpoint =============

@app.patch("/profiles/{profile_id}/scenario_history/{scenario_id}/feedback")
def update_scenario_feedback(profile_id: str, scenario_id: str = Path(...), feedback: str = Body(...), db: Session = Depends(get_db)):
    from models.db_models import ScenarioHistory
    entry = db.query(ScenarioHistory).filter_by(id=scenario_id, profile_id=profile_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Scenario history entry not found")
    entry.feedback = feedback
    db.commit()
    db.refresh(entry)
    return {"id": entry.id, "feedback": entry.feedback}
# ============= Scenario Pin/Unpin Endpoint =============

@app.patch("/profiles/{profile_id}/scenario_history/{scenario_id}/pin")
def pin_scenario_history_entry(profile_id: str, scenario_id: str = Path(...), pin: bool = Body(...), db: Session = Depends(get_db)):
    from models.db_models import ScenarioHistory
    entry = db.query(ScenarioHistory).filter_by(id=scenario_id, profile_id=profile_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Scenario history entry not found")
    entry.pinned = bool(pin)
    db.commit()
    db.refresh(entry)
    return {"id": entry.id, "pinned": entry.pinned}
@app.get("/profiles/{profile_id}/action_plan/pdf")
def export_action_plan_pdf(profile_id: str, db: Session = Depends(get_db)):
    """Export a PDF action plan for the profile's recommended actions."""
    profile = crud.get_credit_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    # Compose profile dict for PDF utility
    accounts = [
        {
            "id": acc.id,
            "type": acc.type,
            "name": acc.name,
            "balance": acc.balance,
            "limit": acc.limit,
            "open_date": str(acc.open_date),
            "status": acc.status,
        }
        for acc in profile.accounts
    ]
    profile_dict = {
        "id": profile.id,
        "user_id": profile.user_id,
        "name": getattr(profile, "name", ""),
        "accounts": accounts,
    }
    # Get recommended actions (reuse scenario_engine)
    from scoring.scenarios import ScenarioEngine
    from scoring.fico_engine import FicoEngine
    engine = ScenarioEngine(FicoEngine())
    recs = engine.get_recommendations(profile)
    actions = recs.get("actions", [])
    from utils.pdf_export import generate_action_plan_pdf
    pdf_bytes = generate_action_plan_pdf(profile_dict, actions)
    return Response(pdf_bytes, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=action_plan_{profile_id}.pdf"
    })
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, Query, Body, Response, Path
# ============= Scenario History Notes/Tags Update Endpoint =============

@app.patch("/profiles/{profile_id}/scenario_history/{scenario_id}")
def update_scenario_history_entry(profile_id: str, scenario_id: str = Path(...), data: dict = Body(...), db: Session = Depends(get_db)):
    """Update notes or tags for a scenario history entry."""
    from models.db_models import ScenarioHistory
    entry = db.query(ScenarioHistory).filter_by(id=scenario_id, profile_id=profile_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Scenario history entry not found")
    updated = False
    if 'notes' in data:
        entry.notes = data['notes']
        updated = True
    if 'tags' in data:
        entry.tags = data['tags']
        updated = True
    if updated:
        db.commit()
        db.refresh(entry)
    return {"id": entry.id, "notes": entry.notes, "tags": entry.tags}
@app.get("/profiles/{profile_id}/scenario_comparison/pdf")
def export_scenario_comparison_pdf(profile_id: str, scenario_ids: str = Query(...), db: Session = Depends(get_db)):
    """Export a PDF comparing two scenario history entries for a profile."""
    ids = scenario_ids.split(",")
    if len(ids) != 2:
        raise HTTPException(status_code=400, detail="Exactly two scenario IDs required.")
    entries = get_scenario_history(db, profile_id, limit=200)
    selected = [e for e in entries if str(e.id) in ids]
    if len(selected) != 2:
        raise HTTPException(status_code=404, detail="Scenario(s) not found.")
    # Compose minimal profile dict for PDF utility
    from utils.pdf_export import generate_scenario_comparison_pdf
    pdf_bytes = generate_scenario_comparison_pdf(selected[0], selected[1])
    return Response(pdf_bytes, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=scenario_comparison_{ids[0]}_{ids[1]}.pdf"
    })
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, Query, Body, Response
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
import os
import tempfile
import logging

from scoring.fico_engine import FicoEngine
from scoring.scenarios import ScenarioEngine
from scoring.optimizer import find_best_actions, estimate_score_improvement_timeline
from scoring.scenario_analyzer import (
    calculate_confidence_intervals,
    simulate_multi_action,
    find_optimal_action_sequence,
    generate_action_priority_matrix,
)
from models.database import get_db, init_db
from models import crud
from models.db_models import Account as AccountModel, Derogatory as DerogatoryModel
from utils.credit_report_parser import parse_credit_report, Bureau
from utils.pdf_export import generate_profile_report_pdf
# ============= PDF Export Endpoint =============

@app.get("/profiles/{profile_id}/export/pdf")
def export_profile_pdf(profile_id: str, db: Session = Depends(get_db)):
    """Export a credit profile, score history, and scenario history as a PDF report."""
    profile = crud.get_credit_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Compose profile dict for PDF utility
    accounts = [
        {
            "id": acc.id,
            "type": acc.type,
            "name": acc.name,
            "balance": acc.balance,
            "limit": acc.limit,
            "open_date": str(acc.open_date),
            "status": acc.status,
        }
        for acc in profile.accounts
    ]
    derogatories = [
        {
            "id": der.id,
            "type": der.type,
            "date": str(der.date),
            "details": der.details,
        }
        for der in profile.derogatories
    ]
    profile_dict = {
        "id": profile.id,
        "user_id": profile.user_id,
        "name": getattr(profile, "name", ""),
        "accounts": accounts,
        "derogatories": derogatories,
    }

    # Get score and scenario history
    score_history = crud.get_score_history(db, profile_id)
    score_history_list = [
        {"date": entry.created_at.strftime("%Y-%m-%d"), "score": entry.score}
        for entry in score_history
    ] if score_history else None

    scenario_history = get_scenario_history(db, profile_id, limit=100)
    scenario_history_list = [
        {
            "created_at": str(entry.created_at),
            "actions": entry.actions,
            "simulated_score": entry.simulated_score,
        }
        for entry in scenario_history
    ] if scenario_history else None

    pdf_bytes = generate_profile_report_pdf(profile_dict, score_history_list, scenario_history_list)
    return Response(pdf_bytes, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=profile_{profile_id}_report.pdf"
    })
from models.score_history import save_score_history, get_score_history
from models.scenario_history import save_scenario_history, get_scenario_history


# Configure basic logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger(__name__)


# Auth bypassed for internal use: all endpoints are now public

# Initialize engines
fico_engine = FicoEngine()
scenario_engine = ScenarioEngine(fico_engine)


# ============= Startup Event =============

@app.on_event("startup")
def startup():
    """Initialize database on app startup"""
    init_db()

    # Optionally apply DB migrations at startup. Controlled via environment
    # variable `MIGRATE_ON_STARTUP`. Default is 'false' to avoid accidental
    # schema changes in production-like environments.
    migrate_flag = os.getenv("MIGRATE_ON_STARTUP", "false").lower()
    if migrate_flag in ("1", "true", "yes", "on"):
        try:
            # Import Alembic lazily so tests/environments without Alembic don't fail on import
            from alembic.config import Config as AlembicConfig
            from alembic import command as alembic_command

            alembic_cfg_path = os.path.join(os.path.dirname(__file__), "alembic.ini")
            if not os.path.exists(alembic_cfg_path):
                # fallback to project root alembic.ini
                alembic_cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini")

            cfg = AlembicConfig(alembic_cfg_path)
            # Ensure the script_location points to the bundled `alembic` folder
            cfg.set_main_option("script_location", os.path.join(os.path.dirname(__file__), "alembic"))
            alembic_command.upgrade(cfg, "head")
            logger.info("Applied DB migrations (alembic)")
        except Exception:
            logger.exception("Error applying migrations on startup")

    logger.info("✓ GhostScore API started")


# ============= Routes =============

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "GhostScore API"}


@app.post("/profiles", response_model=ProfileResponse)
def create_profile(request: CreateProfileRequest, db: Session = Depends(get_db)):
    """Create new credit profile for user"""
    user = crud.get_or_create_user(db, request.email)
    profile = crud.create_credit_profile(db, user.id, request.profile_name)
    return {"id": profile.id, "name": profile.name}


@app.get("/profiles/{user_email}")
def get_profiles(user_email: str, db: Session = Depends(get_db)):
    """Get all profiles for user"""
    user = crud.get_or_create_user(db, user_email)
    profiles = crud.get_user_profiles(db, user.id)
    return [{"id": p.id, "name": p.name} for p in profiles]


@app.get("/profiles/{profile_id}/full")
def get_full_profile(profile_id: str, db: Session = Depends(get_db)):
    """Get full profile with all accounts and derogatories"""
    profile = crud.get_credit_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    accounts = [
        Account(
            id=acc.id,
            type=acc.type,
            name=acc.name,
            balance=acc.balance,
            limit=acc.limit,
            open_date=acc.open_date,
            status=acc.status,
        )
        for acc in profile.accounts
    ]
    
    derogatories = [
        Derogatory(
            id=der.id,
            type=der.type,
            date=der.date,
            details=der.details,
        )
        for der in profile.derogatories
    ]
    
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "accounts": accounts,
        "derogatories": derogatories,
    }


@app.get("/profiles/{profile_id}/stability")
def get_profile_stability(profile_id: str, db: Session = Depends(get_db)):
    """Get score stability metrics for a profile"""
    profile = crud.get_credit_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    try:
        # Extract account balances for utilization stability
        balances = [acc.balance for acc in profile.accounts if acc.balance is not None]
        limits = [acc.limit for acc in profile.accounts if acc.limit is not None]
        
        # Calculate utilization rates
        utils = []
        for bal, limit in zip(balances, limits):
            if limit and limit > 0:
                utils.append(bal / limit)
        
        # Calculate stability metrics
        util_stability = float(np.std(utils)) if utils and len(utils) > 1 else 0.0
        
        # Account age stability (binary: 1 if diverse ages existing)
        ages = [acc.open_date for acc in profile.accounts if acc.open_date]
        age_stability = 1.0 if len(set(ages)) > 1 else 0.0
        
        # Derogatory volatility (inverse of stability - more derogs = less stable)
        derog_count = len(profile.derogatories)
        derog_volatility = min(1.0, derog_count / 5.0)  # Normalize by assuming 5+ derogs is worst case
        
        # Stability index
        stability_index = ScoreStabilityIndex().compute(utils) if utils else 0.0
        
        # Overall confidence (inverse of average volatility)
        confidence = float(1.0 - (util_stability + age_stability + derog_volatility) / 3)
        confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1
        
        return {
            "stability_index": round(stability_index, 3),
            "confidence": round(confidence, 3),
            "payment_history_stability": round(1.0 - min(1.0, derog_volatility), 3),
            "utilization_stability": round(1.0 - util_stability, 3),
            "account_age_stability": round(age_stability, 3),
            "derogatory_volatility": round(derog_volatility, 3),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error computing stability: {str(e)}")


@app.post("/profiles/{profile_id}/accounts")
def add_account(profile_id: str, account: Account, db: Session = Depends(get_db)):
    """Add account to profile"""
    profile = crud.get_credit_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    new_account = crud.create_account(
        db,
        profile_id=profile_id,
        type=account.type,
        name=account.name,
        balance=account.balance,
        limit=account.limit,
        open_date=account.open_date,
        status=account.status,
    )
    return {"id": new_account.id, "name": new_account.name}


@app.delete("/profiles/{profile_id}/accounts/{account_id}")
def delete_account(profile_id: str, account_id: str, db: Session = Depends(get_db)):
    """Delete a specific account from a profile"""
    try:
        from models.db_models import CreditProfile as CreditProfileModel, Account
        
        # Verify profile exists
        profile = db.query(CreditProfileModel).filter(CreditProfileModel.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Delete the account
        account = db.query(Account).filter(
            Account.id == account_id,
            Account.profile_id == profile_id
        ).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        db.delete(account)
        db.commit()
        
        return {"deleted": True, "account_id": account_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/profiles/{profile_id}/accounts-all")
def delete_all_accounts(profile_id: str, db: Session = Depends(get_db)):
    """Delete ALL accounts from a profile (useful for clearing bad imports)"""
    try:
        from models.db_models import CreditProfile as CreditProfileModel, Account
        
        # Verify profile exists
        profile = db.query(CreditProfileModel).filter(CreditProfileModel.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Count and delete all accounts
        count = db.query(Account).filter(Account.profile_id == profile_id).count()
        
        db.query(Account).filter(Account.profile_id == profile_id).delete()
        db.commit()
        
        print(f"Deleted {count} accounts from profile {profile_id}")
        
        return {"deleted": count, "message": f"Successfully deleted {count} account(s)"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/profiles/{profile_id}/derogatories")
def add_derogatory(profile_id: str, derog: Derogatory, db: Session = Depends(get_db)):
    """Add derogatory mark to profile"""
    profile = crud.get_credit_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    new_derog = crud.create_derogatory(
        db,
        profile_id=profile_id,
        type=derog.type,
        date_val=derog.date,
        details=derog.details,
    )
    return {"id": new_derog.id, "type": new_derog.type}


@app.post("/debug/score")
def debug_score(profile: CreditProfile):
    """Debug endpoint to see what the profile looks like"""
    try:
        engine = fico_engine
        result = engine.calculate_full_score(profile)
        return {
            "success": True,
            "result_type": str(type(result)),
            "result_keys": list(result.keys()) if isinstance(result, dict) else "Not a dict",
            "score": result.get('score', 'N/A') if isinstance(result, dict) else "N/A",
        }
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
        }

@app.post("/score", response_model=ScoreResponse)
def calculate_score(profile: CreditProfile, model: Optional[str] = None):
    """Calculate FICO score and subscores. Optional `model` query parameter selects scoring model (e.g., `fico8`)."""
    try:
        # Get the appropriate engine
        engine = FicoEngine(model) if model else fico_engine
        
        # Calculate full score (includes subscores)
        result = engine.calculate_full_score(profile)
        
        # Return just the required fields as ScoreResponse
        return {
            'score': int(result.get('score', 0)),
            'payment_history': int(result.get('payment_history', 50)),
            'utilization': int(result.get('utilization', 50)),
            'age': int(result.get('age', 50)),
            'new_credit': int(result.get('new_credit', 50)),
            'mix': int(result.get('mix', 50)),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/simulate/paydown")
def simulate_paydown(request: ScenarioRequest):
    """Simulate score change from paying down an account"""
    try:
        result = scenario_engine.simulate_paydown(
            request.profile,
            request.account_id,
            request.new_balance
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/simulate/multiple")
def simulate_multiple(request: dict):
    """Simulate multiple scenarios"""
    profile = CreditProfile(**request.get("profile", {}))
    scenarios = request.get("scenarios", [])
    
    try:
        results = scenario_engine.simulate_multiple_scenarios(profile, scenarios)
        return {"scenarios": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/recommendations", response_model=dict)
def get_recommendations(profile: CreditProfile):
    """Get optimization recommendations"""
    try:
        recommendations = scenario_engine.get_recommendations(profile)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/optimize")
def optimize_credit_profile(profile: CreditProfile, model: Optional[str] = None):
    """
    Find the best actions to improve credit score.
    
    Uses the optimizer engine to:
    1. Rank actions by score impact
    2. Estimate improvement timeline
    3. Identify quick wins
    
    Returns:
        {
            "current_score": int,
            "scorecard": str,
            "recommended_actions": [action1, action2, ...],
            "improvement_timeline": [week0, week2, week4, ...],
            "total_potential_gain": int
        }
    """
    try:
        # Convert profile to dict for optimizer (supports both ORM and dict)
        profile_dict = {
            "accounts": [
                {
                    "id": acc.id,
                    "type": acc.type,
                    "name": acc.name,
                    "balance": acc.balance,
                    "limit": acc.limit,
                    "open_date": str(acc.open_date) if acc.open_date else None,
                    "status": acc.status,
                }
                for acc in profile.accounts
            ],
            "derogatories": [
                {
                    "type": derog.type,
                    "date": str(derog.date) if derog.date else None,
                    "details": derog.details,
                }
                for derog in profile.derogatories
            ] if profile.derogatories else [],
        }
        
        # Use requested scoring model for this optimization request
        engine = FicoEngine(model) if model else fico_engine

        # Get full score info (includes scorecard)
        score_info = engine.calculate_full_score(profile_dict)

        # Find best actions
        actions = find_best_actions(profile_dict, engine.calculate_score)

        # Estimate improvement timeline
        timeline = estimate_score_improvement_timeline(
            profile_dict,
            actions,
            engine.calculate_score
        )
        
        # Calculate total potential gain using new field name
        total_gain = sum(a.get("estimated_gain", 0) for a in actions)
        
        return {
            "current_score": score_info['score'],
            "scorecard": score_info['scorecard'],
            "scorecard_description": score_info['scorecard_description'],
            "recommended_actions": actions,
            "improvement_timeline": timeline,
            "total_potential_gain": total_gain,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/scenarios/multi-action")
def simulate_multi_action_scenario(data: dict):
    """
    Simulate multiple credit improvement actions applied simultaneously.
    
    Returns:
        {
            "original_score": int,
            "simulated_score": int,
            "actual_gain": int,
            "actions_applied": [...],
            "timeline": [...]
        }
    """
    try:
        profile_dict = data.get("profile", {})
        action_indices = data.get("action_indices", [])
        
        # Get optimizer recommendations
        actions = find_best_actions(profile_dict, fico_engine.calculate_score)
        
        # Simulate multi-action scenario
        result = simulate_multi_action(
            profile_dict,
            action_indices,
            actions,
            fico_engine.calculate_score
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/scenarios/confidence-intervals")
def get_confidence_intervals(data: dict):
    """
    Calculate optimistic, realistic, and conservative score projections.
    
    Returns:
        {
            "optimistic": {"score": int, "gain": int, "confidence": float},
            "realistic": {"score": int, "gain": int, "confidence": float},
            "conservative": {"score": int, "gain": int, "confidence": float}
        }
    """
    try:
        profile_dict = data.get("profile", {})
        
        # Get current score
        current_score_info = fico_engine.calculate_full_score(profile_dict)
        current_score = current_score_info['score']
        
        # Get recommendations
        actions = find_best_actions(profile_dict, fico_engine.calculate_score)
        
        # Calculate confidence intervals
        scenarios = calculate_confidence_intervals(
            current_score,
            actions,
            fico_engine.calculate_score
        )
        
        return {
            "current_score": current_score,
            "optimistic": scenarios['optimistic'],
            "realistic": scenarios['realistic'],
            "conservative": scenarios['conservative'],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/scenarios/optimal-sequence")
def get_optimal_action_sequence(data: dict):
    """
    Find the optimal sequence of actions to maximize score gain efficiency.
    
    Considers both score impact and implementation effort/cost.
    
    Returns:
        {
            "recommended_sequence": [action_indices],
            "expected_gain": int,
            "efficiency_score": float,
            "priority_matrix": {
                "quick_wins": [...],
                "strategic": [...],
                "fill_ins": [...],
                "avoid": [...]
            }
        }
    """
    try:
        profile_dict = data.get("profile", {})
        max_budget = data.get("max_budget", None)
        
        # Get recommendations
        actions = find_best_actions(profile_dict, fico_engine.calculate_score)
        
        # Find optimal sequence
        optimal_indices, expected_gain, efficiency = find_optimal_action_sequence(
            profile_dict,
            actions,
            fico_engine.calculate_score,
            max_cost=max_budget
        )
        
        # Generate priority matrix
        priority_matrix = generate_action_priority_matrix(actions)
        
        return {
            "recommended_sequence": optimal_indices,
            "expected_gain": expected_gain,
            "efficiency_score": efficiency,
            "priority_matrix": {
                "quick_wins": [a for a in priority_matrix['quick_wins']],
                "strategic": [a for a in priority_matrix['strategic']],
                "fill_ins": [a for a in priority_matrix['fill_ins']],
                "avoid": [a for a in priority_matrix['avoid']],
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/profiles/{profile_id}/score_history")
def get_score_history(profile_id: str, db: Session = Depends(get_db), limit: int = 100):
    """Get score history for a profile"""
    try:
        history = crud.get_score_history(db, profile_id)
        if not history:
            return []
        
        # Format response as date and score
        return [
            {
                "date": entry.created_at.strftime("%Y-%m-%d"),
                "score": entry.score
            }
            for entry in history
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/profiles/{profile_id}/score_history")
def save_score_snapshot(profile_id: str, score_data: dict, db: Session = Depends(get_db)):
    """Save a score snapshot for a profile"""
    try:
        from models.score_history import ScoreHistory as ScoreHistoryModel
        
        score = score_data.get('score') if isinstance(score_data, dict) else int(score_data)
        
        history_entry = ScoreHistoryModel(
            profile_id=profile_id,
            score=score
        )
        
        db.add(history_entry)
        db.commit()
        db.refresh(history_entry)
        
        return {"id": history_entry.id, "saved": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/profiles/{profile_id}/upload-credit-report", response_model=CreditReportUploadResponse)
def upload_credit_report(
    profile_id: str,
    bureau: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and parse credit report from Equifax, Experian, or Transunion"""
    try:
        print(f"\n=== UPLOAD START ===")
        print(f"Profile ID: {profile_id}")
        print(f"Bureau: {bureau}")
        print(f"File: {file.filename}")
        
        # Validate bureau
        bureau_lower = bureau.lower()
        if bureau_lower not in [b.value for b in Bureau]:
            raise HTTPException(status_code=400, detail=f"Invalid bureau: {bureau}. Must be equifax, experian, or transunion")
        
        # Validate profile exists
        from models.db_models import CreditProfile as CreditProfileModel
        existing = db.query(CreditProfileModel).filter(CreditProfileModel.id == profile_id).first()
        if not existing:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        print(f"Profile found: {existing.name}")
        
        # Save uploaded file temporarily
        print(f"Reading file...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = file.file.read()
            print(f"File size: {len(content)} bytes")
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        print(f"Temp file saved to: {tmp_path}")
        
        try:
            # Parse the credit report
            print(f"Starting parsing...")
            accounts, status = parse_credit_report(tmp_path, Bureau(bureau_lower))
            
            print(f"Parsing complete. Extracted {len(accounts)} accounts. Status: {status}")
            
            # Convert to ExtractedAccount format
            extracted = [
                ExtractedAccount(
                    name=acc.get('name', 'Unknown'),
                    type=acc.get('type', 'other'),
                    balance=float(acc.get('balance', 0)),
                    limit=float(acc.get('limit')) if acc.get('limit') else None,
                    open_date=acc.get('open_date', date.today().isoformat()),
                    status=acc.get('status', 'active')
                )
                for acc in accounts
            ]
            
            print(f"Returning {len(extracted)} extracted accounts")
            print(f"=== UPLOAD SUCCESS ===\n")
            
            return CreditReportUploadResponse(
                accounts=extracted,
                status=status
            )
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                print(f"Temp file cleaned up")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"=== UPLOAD ERROR ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"=== END ERROR ===\n")
        raise HTTPException(status_code=400, detail=f"Error processing credit report: {str(e)}")


@app.post("/profiles/{profile_id}/import-accounts-from-report")
def import_accounts_from_report(
    profile_id: str,
    request: ImportAccountsRequest,
    db: Session = Depends(get_db)
):
    """Import selected accounts from credit report into profile"""
    try:
        # Validate profile exists
        from models.db_models import CreditProfile as CreditProfileModel
        profile_obj = db.query(CreditProfileModel).filter(CreditProfileModel.id == profile_id).first()
        if not profile_obj:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Determine which accounts to import
        accounts_to_import = request.accounts
        if request.selected_indices is not None:
            accounts_to_import = [request.accounts[i] for i in request.selected_indices if i < len(request.accounts)]
        
        # Import each account with validation and duplicate-detection
        imported_count = 0
        imported_accounts = []
        skipped_duplicates = []
        invalid_accounts = []

        for acc in accounts_to_import:
            try:
                acc_dict = acc.dict() if hasattr(acc, 'dict') else dict(acc)

                # Server-side validation
                valid, msg = crud.validate_account_payload(acc_dict)
                if not valid:
                    invalid_accounts.append({"account": acc_dict, "reason": msg})
                    continue

                # Duplicate detection
                duplicate = crud.find_similar_account(db, profile_id, acc_dict.get('name'), acc_dict.get('type'))
                if duplicate:
                    skipped_duplicates.append({"existing_id": duplicate.id, "name": duplicate.name})
                    continue

                # Parse open_date to date if provided
                open_date_val = None
                if acc_dict.get('open_date'):
                    try:
                        from datetime import date as date_cls
                        open_date_val = date_cls.fromisoformat(acc_dict.get('open_date'))
                    except Exception:
                        open_date_val = None

                # Create account in database
                account = crud.create_account(
                    db=db,
                    profile_id=profile_id,
                    type=acc_dict.get('type', 'other'),
                    name=acc_dict.get('name'),
                    balance=float(acc_dict.get('balance', 0)),
                    limit=float(acc_dict.get('limit')) if acc_dict.get('limit') else None,
                    open_date=open_date_val,
                    status=acc_dict.get('status', 'active')
                )
                imported_accounts.append({
                    "id": account.id,
                    "name": account.name,
                    "type": account.type
                })
                imported_count += 1
            except Exception as e:
                print(f"Error importing account {getattr(acc, 'name', None)}: {str(e)}")
                continue

        return {
            "imported_count": imported_count,
            "total_count": len(accounts_to_import),
            "accounts": imported_accounts,
            "skipped_duplicates": skipped_duplicates,
            "invalid_accounts": invalid_accounts,
            "message": f"Successfully imported {imported_count} of {len(accounts_to_import)} accounts"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error importing accounts: {str(e)}")


@app.post("/debug/extract-pdf-text")
def debug_extract_pdf_text(file: UploadFile = File(...)):
    """DEBUG: Extract and return raw text from PDF"""
    try:
        import tempfile
        import os
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = file.file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            from utils.credit_report_parser import extract_text_from_pdf
            
            text = extract_text_from_pdf(tmp_path)
            
            # Return first 5000 chars so we can see the format
            return {
                "file_name": file.filename,
                "file_size": len(content),
                "text_extracted": len(text),
                "first_1000_chars": text[:1000],
                "account_patterns_found": {
                    "creditor": len(re.findall(r'creditor\s*[:\-]', text, re.IGNORECASE)),
                    "account": len(re.findall(r'account\s*[:\-]', text, re.IGNORECASE)),
                    "balance": len(re.findall(r'balance\s*[:\-]', text, re.IGNORECASE)),
                    "credit_karma": len(re.findall(r'credit karma', text, re.IGNORECASE)),
                }
            }
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@app.post("/profiles/{profile_id}/scenario_history", response_model=ScenarioHistoryEntry)
def save_scenario_run(profile_id: str, data: dict = Body(...), db: Session = Depends(get_db)):
    """Save a scenario run for a profile (for scenario history and comparison)"""
    try:
        entry = save_scenario_history(
            db,
            profile_id=profile_id,
            actions=data.get("actions", []),
            original_score=data.get("original_score"),
            simulated_score=data.get("simulated_score"),
            actual_gain=data.get("actual_gain"),
            timeline=data.get("timeline"),
            notes=data.get("notes"),
        )
        return entry
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/profiles/{profile_id}/scenario_history", response_model=List[ScenarioHistoryEntry])
def get_scenario_history_api(profile_id: str, limit: int = Query(100, le=500), db: Session = Depends(get_db)):
    """Get scenario history for a profile (for scenario comparison and tracking)"""
    try:
        entries = get_scenario_history(db, profile_id, limit)
        return entries
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

