"""
Feature Extraction Layer

Normalizes credit profile into a standardized feature set.
This is the foundation for all downstream scoring models.
"""

from datetime import datetime, date
from typing import Dict, List, Any


def extract_features(profile: Dict[str, Any]) -> Dict[str, float]:
    """
    Extract normalized features from a credit profile.
    
    Converts raw account and derogatory data into standardized
    features used by all scoring models.
    
    Args:
        profile: Credit profile dict with 'accounts' and 'derogatories' keys
        
    Returns:
        Dict of normalized features (0-1 or specific ranges)
    """
    accounts = profile.get("accounts", [])
    derogatories = profile.get("derogatories", [])
    
    # Separate by account type
    revolving = [a for a in accounts if a.get("type") == "credit_card"]
    installment = [a for a in accounts if a.get("type") in ("auto_loan", "personal_loan")]
    mortgage = [a for a in accounts if a.get("type") == "mortgage"]
    
    # === Utilization Features ===
    total_revolving_balance = sum(float(a.get("balance", 0)) for a in revolving)
    total_revolving_limit = sum(float(a.get("limit", 0)) for a in revolving if a.get("limit"))
    
    utilization = (
        total_revolving_balance / total_revolving_limit 
        if total_revolving_limit > 0 else 0
    )
    
    # Max utilization on any single card
    max_util = max(
        (float(a.get("balance", 0)) / float(a.get("limit", 1)) 
         for a in revolving if a.get("limit")),
        default=0
    )
    
    # === Age Features ===
    now = datetime.now()
    account_ages = []
    
    for acc in accounts:
        try:
            open_date = datetime.fromisoformat(str(acc.get("open_date")))
            age_years = (now - open_date).days / 365.25
            account_ages.append(age_years)
        except (ValueError, TypeError):
            pass
    
    avg_age = sum(account_ages) / len(account_ages) if account_ages else 0
    oldest_age = max(account_ages, default=0)
    youngest_age = min(account_ages, default=0) if account_ages else 0
    
    # === Account Count & Mix Features ===
    total_accounts = len(accounts)
    revolving_count = len(revolving)
    installment_count = len(installment)
    mortgage_count = len(mortgage)
    closed_accounts = len([a for a in accounts if a.get("status") == "closed"])
    
    # Credit mix (variety of account types)
    mix_score = sum([
        1 if revolving_count > 0 else 0,
        1 if installment_count > 0 else 0,
        1 if mortgage_count > 0 else 0,
    ]) / 3.0  # 0-1 score
    
    # === Derogatory Features ===
    derogatory_count = len(derogatories)
    
    # Recency of most recent derogatory
    days_since_derogatory = 999999
    if derogatories:
        try:
            derog_dates = []
            for d in derogatories:
                derog_date = d.get("date")
                if isinstance(derog_date, str):
                    derog_date = datetime.fromisoformat(derog_date).date()
                if isinstance(derog_date, date):
                    derog_dates.append((now.date() - derog_date).days)
            
            if derog_dates:
                days_since_derogatory = min(derog_dates)
        except (ValueError, TypeError):
            pass
    
    # Severity (count by type)
    bankruptcy_count = len([d for d in derogatories if d.get("type") == "bankruptcy"])
    charge_off_count = len([d for d in derogatories if d.get("type") == "charge_off"])
    collection_count = len([d for d in derogatories if d.get("type") == "collection"])
    late_payment_count = len([d for d in derogatories if d.get("type") == "late_payment"])
    
    # === Compile Feature Vector ===
    features = {
        # Utilization (0-1)
        "utilization": min(utilization, 1.0),
        "max_utilization": min(max_util, 1.0),
        
        # Age (years)
        "avg_age": avg_age,
        "oldest_age": oldest_age,
        "youngest_age": youngest_age,
        
        # Account counts
        "total_accounts": total_accounts,
        "revolving_count": revolving_count,
        "installment_count": installment_count,
        "mortgage_count": mortgage_count,
        "closed_accounts": closed_accounts,
        
        # Mix (0-1)
        "credit_mix": mix_score,
        
        # Derogatory
        "derogatory_count": derogatory_count,
        "bankruptcy_count": bankruptcy_count,
        "charge_off_count": charge_off_count,
        "collection_count": collection_count,
        "late_payment_count": late_payment_count,
        "days_since_derogatory": days_since_derogatory,
        
        # Balances
        "total_revolving_balance": total_revolving_balance,
        "total_revolving_limit": total_revolving_limit,
    }
    
    return features
