"""
CRUD operations for database models
"""

from sqlalchemy.orm import Session
from models.db_models import User, CreditProfile, Account, Derogatory, ScoreHistory
from datetime import date


# ============ User Operations ============

def get_or_create_user(db: Session, email: str):
    """Get user by email or create new one"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str):
    """Get user by email (no create)"""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, hashed_password: str):
    """Create a new user with hashed password"""
    user = User(email=email, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: str):
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


# ============ Credit Profile Operations ============

def create_credit_profile(db: Session, user_id: str, name: str = None):
    """Create new credit profile for user"""
    profile = CreditProfile(user_id=user_id, name=name or "Profile")
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_credit_profile(db: Session, profile_id: str):
    """Get credit profile by ID"""
    return db.query(CreditProfile).filter(CreditProfile.id == profile_id).first()


def get_user_profiles(db: Session, user_id: str):
    """Get all profiles for user"""
    return db.query(CreditProfile).filter(CreditProfile.user_id == user_id).all()


def delete_credit_profile(db: Session, profile_id: str):
    """Delete credit profile"""
    profile = db.query(CreditProfile).filter(CreditProfile.id == profile_id).first()
    if profile:
        db.delete(profile)
        db.commit()
    return profile


# ============ Account Operations ============

def create_account(
    db: Session,
    profile_id: str,
    type: str,
    name: str,
    balance: float,
    limit: float = None,
    open_date: date = None,
    status: str = "active",
):
    """Create new account"""
    account = Account(
        profile_id=profile_id,
        type=type,
        name=name,
        balance=balance,
        limit=limit,
        open_date=open_date or date.today(),
        status=status,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get_account(db: Session, account_id: str):
    """Get account by ID"""
    return db.query(Account).filter(Account.id == account_id).first()


def get_profile_accounts(db: Session, profile_id: str):
    """Get all accounts for profile"""
    return db.query(Account).filter(Account.profile_id == profile_id).all()


def find_similar_account(db: Session, profile_id: str, name: str, account_type: str = None):
    """Find an account in the profile that is likely the same as the provided one.

    This is a lightweight duplicate-detection: checks for case-insensitive name equality
    or name containment and (optionally) same account type.
    """
    if not name:
        return None
    name_lower = name.strip().lower()
    query = db.query(Account).filter(Account.profile_id == profile_id)
    candidates = query.all()
    for c in candidates:
        if not c.name:
            continue
        existing = c.name.strip().lower()
        # exact match
        if existing == name_lower:
            return c
        # existing contains new or new contains existing (substring match)
        if existing in name_lower or name_lower in existing:
            # if types are provided, prefer matching types
            if account_type:
                if getattr(c, 'type', None) == account_type:
                    return c
                # otherwise still consider as duplicate
                return c
            return c
    return None


def update_account(db: Session, account_id: str, **kwargs):
    """Update account"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if account:
        for key, value in kwargs.items():
            if hasattr(account, key):
                setattr(account, key, value)
        db.commit()
        db.refresh(account)
    return account


def delete_account(db: Session, account_id: str):
    """Delete account"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if account:
        db.delete(account)
        db.commit()
    return account


def validate_account_payload(account: dict) -> tuple[bool, str]:
    """Simple server-side validation for incoming account payloads.

    Returns (is_valid, message)
    """
    if 'name' not in account or not account['name']:
        return False, 'Account name is required'
    if 'balance' not in account:
        return False, 'Balance is required'
    try:
        float(account.get('balance', 0))
    except Exception:
        return False, 'Balance must be a number'
    if 'open_date' in account and account['open_date']:
        try:
            # Accept YYYY-MM-DD
            from datetime import datetime
            datetime.fromisoformat(account['open_date'])
        except Exception:
            return False, 'open_date must be YYYY-MM-DD'
    return True, 'ok'


# ============ Derogatory Operations ============

def create_derogatory(
    db: Session,
    profile_id: str,
    type: str,
    date_val: date,
    details: str = None,
):
    """Create new derogatory mark"""
    derogatory = Derogatory(
        profile_id=profile_id,
        type=type,
        date=date_val,
        details=details,
    )
    db.add(derogatory)
    db.commit()
    db.refresh(derogatory)
    return derogatory


def get_derogatory(db: Session, derogatory_id: str):
    """Get derogatory by ID"""
    return db.query(Derogatory).filter(Derogatory.id == derogatory_id).first()


def get_profile_derogatories(db: Session, profile_id: str):
    """Get all derogatories for profile"""
    return db.query(Derogatory).filter(Derogatory.profile_id == profile_id).all()


def delete_derogatory(db: Session, derogatory_id: str):
    """Delete derogatory"""
    derogatory = db.query(Derogatory).filter(Derogatory.id == derogatory_id).first()
    if derogatory:
        db.delete(derogatory)
        db.commit()
    return derogatory


# ============ Score History Operations ============

def save_score_history(
    db: Session,
    profile_id: str,
    score: int,
    payment_history: int = None,
    utilization: int = None,
    age: int = None,
    new_credit: int = None,
    mix: int = None,
):
    """Save score calculation to history"""
    history = ScoreHistory(
        profile_id=profile_id,
        score=score,
        payment_history=payment_history,
        utilization=utilization,
        age=age,
        new_credit=new_credit,
        mix=mix,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def get_score_history(db: Session, profile_id: str, limit: int = 30):
    """Get score history for profile"""
    return (
        db.query(ScoreHistory)
        .filter(ScoreHistory.profile_id == profile_id)
        .order_by(ScoreHistory.created_at.desc())
        .limit(limit)
        .all()
    )
