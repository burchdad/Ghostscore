from scoring.score_forecast_ml import ml_score_forecaster
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
        # Extract features from profile
        from scoring.feature_engine import extract_features
        features = extract_features(request.profile.dict() if hasattr(request.profile, 'dict') else request.profile)
        forecast = ml_score_forecaster.predict(features, weeks=request.weeks)
        return {"forecast": forecast, "weeks": request.weeks}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
from pydantic import BaseModel

# ============= Strategy Optimization Endpoint =============
class OptimizeGoalRequest(BaseModel):
    profile: dict
    target_score: int
    budget: float | None = None
    timeline_weeks: int | None = None

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
from scoring.calibration_engine import update_correction, apply_calibration
# ============= Calibration Endpoints =============

from pydantic import BaseModel

class CalibrationRequest(BaseModel):
    estimated_score: float
    actual_score: float

@app.post("/profiles/{profile_id}/calibrate")
def calibrate_profile(profile_id: str, req: CalibrationRequest):
    """Submit actual score for a profile to calibrate future estimates."""
    update_correction(profile_id, req.estimated_score, req.actual_score)
    return {"profile_id": profile_id, "correction": req.actual_score - req.estimated_score}

@app.get("/profiles/{profile_id}/calibrated-score")
def get_calibrated_score(profile_id: str, estimated_score: float):
    """Get a calibrated score estimate for a profile."""
    corrected = apply_calibration(profile_id, estimated_score)
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
from fastapi.middleware.cors import CORSMiddleware
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


app = FastAPI(title="GhostScore API", version="0.1.0")

# Configure basic logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger(__name__)


# Auth bypassed for internal use: all endpoints are now public

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    accounts: List[ExtractedAccount]
    status: str
    bureau: str


class ImportAccountsRequest(BaseModel):
    """Request to import accounts from upload"""
    accounts: List[ExtractedAccount]
    selected_indices: List[int] = None  # If None, import all


class ScoreHistoryEntry(BaseModel):
    id: str
    profile_id: str
    score: int
    payment_history: Optional[int]
    utilization: Optional[int]
    age: Optional[int]
    new_credit: Optional[int]
    mix: Optional[int]
    created_at: date

    class Config:
        orm_mode = True


class ScenarioHistoryEntry(BaseModel):
    id: str
    profile_id: str
    actions: list
    original_score: int
    simulated_score: int
    actual_gain: int | None = None
    timeline: list | None = None
    notes: str | None = None
    created_at: date

    class Config:
        orm_mode = True


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


@app.post("/score", response_model=ScoreResponse)
def calculate_score(profile: CreditProfile, model: Optional[str] = None):
    """Calculate FICO score and subscores. Optional `model` query parameter selects scoring model (e.g., `fico8`)."""
    try:
        # Create a local engine using requested model when provided so requests
        # can choose `fico8` or the default linear model.
        engine = FicoEngine(model) if model else fico_engine
        result = engine.calculate_full_score(profile)
        return result
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


@app.get("/profiles/{profile_id}/score-history")
def get_score_history(profile_id: str, db: Session = Depends(get_db)):
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


@app.post("/profiles/{profile_id}/upload-credit-report", response_model=CreditReportUploadResponse)
def upload_credit_report(
    profile_id: str,
    bureau: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and parse credit report from Equifax, Experian, or Transunion"""
    try:
        # Validate bureau
        bureau_lower = bureau.lower()
        if bureau_lower not in [b.value for b in Bureau]:
            raise HTTPException(status_code=400, detail=f"Invalid bureau: {bureau}. Must be equifax, experian, or transunion")
        
        # Validate profile exists
        profile_obj = db.query(AccountModel.__table__.select().where(AccountModel.profile_id == profile_id).scalar_subquery()).first()
        if not profile_obj:
            # Check if profile exists in profiles table
            from models.db_models import CreditProfile as CreditProfileModel
            existing = db.query(CreditProfileModel).filter(CreditProfileModel.id == profile_id).first()
            if not existing:
                raise HTTPException(status_code=404, detail="Profile not found")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = file.file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Parse the credit report
            accounts, status = parse_credit_report(tmp_path, Bureau(bureau_lower))
            
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
            
            return CreditReportUploadResponse(
                accounts=extracted,
                status=status,
                bureau=bureau_lower
            )
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except HTTPException:
        raise
    except Exception as e:
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

