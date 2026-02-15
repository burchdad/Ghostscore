from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
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


app = FastAPI(title="GhostScore API", version="0.1.0")

# Configure basic logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger(__name__)

# auth routes
from auth import router as auth_router, get_current_user
app.include_router(auth_router)


@app.get("/users/me")
def read_current_user(current_user=Depends(get_current_user)):
    """Return the current authenticated user's basic info"""
    return {"id": current_user.id, "email": current_user.email}

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
def calculate_score(profile: CreditProfile):
    """Calculate FICO score and subscores"""
    try:
        result = fico_engine.calculate_full_score(profile)
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
def optimize_credit_profile(profile: CreditProfile):
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
        
        # Get full score info (includes scorecard)
        score_info = fico_engine.calculate_full_score(profile_dict)
        
        # Find best actions
        actions = find_best_actions(profile_dict, fico_engine.calculate_score)
        
        # Estimate improvement timeline
        timeline = estimate_score_improvement_timeline(
            profile_dict,
            actions,
            fico_engine.calculate_score
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

