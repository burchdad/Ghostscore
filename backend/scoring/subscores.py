from datetime import datetime, date, timedelta
from typing import List

def calculate_payment_history_score(accounts, derogatories):
    """
    Payment history accounts for 35% of FICO score.
    
    Factors:
    - Payment account status (on-time vs late)
    - Severity and recency of late payments
    - Number of derogatory marks
    - Public records (bankruptcy, tax liens, judgments)
    
    Returns: 0-100 score
    """
    if not accounts and not derogatories:
        return 100.0
    
    score = 100.0
    
    # Count derogatory items and apply penalties
    if derogatories:
        for derog in derogatories:
            days_ago = (date.today() - derog.date).days
            
            if derog.type == "bankruptcy":
                if days_ago < 365 * 7:  # Within 7 years
                    score -= 50
                else:
                    score -= 10
            elif derog.type == "charge_off":
                if days_ago < 365 * 7:
                    score -= 40
                else:
                    score -= 10
            elif derog.type == "collection":
                if days_ago < 365 * 3:
                    score -= 35
                else:
                    score -= 15
            elif derog.type == "late_payment":
                # Later penalties for late payments
                if days_ago < 30:
                    score -= 25  # Recent
                elif days_ago < 90:
                    score -= 20
                elif days_ago < 180:
                    score -= 15
                elif days_ago < 365 * 2:
                    score -= 10
                else:
                    score -= 5
    
    # Count closed/inactive accounts (slight penalty)
    closed_accounts = [acc for acc in accounts if acc.status == "closed"]
    if closed_accounts:
        score -= min(len(closed_accounts) * 2, 10)
    
    return max(score, 10.0)


def calculate_utilization_score(accounts):
    """
    Credit utilization accounts for 30% of FICO score.
    
    Ideal utilization: < 10%
    Good: < 30%
    Fair: 30-50%
    Poor: > 50%
    
    Returns: 0-100 score
    """
    # Only count revolving accounts (credit cards)
    credit_cards = [acc for acc in accounts if acc.type == "credit_card" and acc.limit]
    
    if not credit_cards:
        return 100.0
    
    total_balance = sum(acc.balance for acc in credit_cards)
    total_limit = sum(acc.limit for acc in credit_cards if acc.limit)
    
    if total_limit == 0:
        return 50.0
    
    utilization = total_balance / total_limit
    
    # Score based on utilization buckets (matches known FICO behavior)
    if utilization <= 0.01:
        return 100.0
    elif utilization <= 0.09:
        return 95.0
    elif utilization <= 0.29:
        return 85.0
    elif utilization <= 0.49:
        return 70.0
    elif utilization <= 0.74:
        return 50.0
    elif utilization <= 0.99:
        return 30.0
    else:
        return 10.0


def calculate_age_score(accounts):
    """
    Age of credit accounts for 15% of FICO score.
    
    Older accounts are better (shows long history).
    Average account age and oldest account matter.
    
    Returns: 0-100 score
    """
    if not accounts:
        return 50.0
    
    today = date.today()
    ages = []
    
    for account in accounts:
        age_days = (today - account.open_date).days
        ages.append(age_days)
    
    if not ages:
        return 50.0
    
    average_age_years = sum(ages) / len(ages) / 365.25
    oldest_age_years = max(ages) / 365.25
    
    # Score based on average account age
    if average_age_years >= 15:
        return 100.0
    elif average_age_years >= 10:
        return 90.0
    elif average_age_years >= 5:
        return 75.0
    elif average_age_years >= 2:
        return 60.0
    elif average_age_years >= 1:
        return 50.0
    elif average_age_years >= 0.5:
        return 40.0
    else:
        return 30.0


def calculate_new_credit_score(accounts):
    """
    New credit accounts for 10% of FICO score.
    
    Too many new accounts in short time = risk (suggests desperation for credit).
    Recent inquiries also impact this.
    
    Returns: 0-100 score
    """
    if not accounts:
        return 100.0
    
    today = date.today()
    recent_accounts = 0
    
    for account in accounts:
        age_days = (today - account.open_date).days
        
        # Count accounts opened in last 2 years
        if age_days < 365 * 2:
            recent_accounts += 1
    
    # Score based on recent account activity
    if recent_accounts == 0:
        return 100.0
    elif recent_accounts == 1:
        return 90.0
    elif recent_accounts == 2:
        return 75.0
    elif recent_accounts <= 4:
        return 60.0
    else:
        return 40.0


def calculate_mix_score(accounts):
    """
    Credit mix accounts for 10% of FICO score.
    
    Having different types of credit (installment, revolving) is good.
    
    Returns: 0-100 score
    """
    if not accounts:
        return 50.0
    
    account_types = set()
    
    # Categorize accounts
    revolving_types = {"credit_card"}
    installment_types = {"loan", "mortgage", "auto_loan"}
    
    for account in accounts:
        if account.type in revolving_types:
            account_types.add("revolving")
        elif account.type in installment_types:
            account_types.add("installment")
        else:
            account_types.add("other")
    
    # Score based on mix
    if len(account_types) >= 3:
        return 100.0
    elif len(account_types) == 2:
        return 85.0
    else:
        return 60.0
