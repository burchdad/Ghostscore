"""
FICO Score Calculator Engine - Orchestrator Pattern

Uses a 4-layer architecture:
  1. Feature Extraction Layer (normalize profiles)
  2. Scorecard Segmentation Layer (assign profile type)
  3. Factor Calculation Layer (subscores)
  4. Aggregation Layer (combine into final score)
"""

from typing import Dict, Any, Union
from datetime import datetime, timedelta
from .feature_engine import extract_features
from .scorecards import determine_scorecard, get_scorecard_description
from .subscores import (
    calculate_payment_history_score,
    calculate_utilization_score,
    calculate_age_score,
    calculate_new_credit_score,
    calculate_mix_score
)
from .aggregator import aggregate_score, calculate_score_details


class DictAccount:
    """Adapter to make dict accounts compatible with ORM-based subscores functions."""
    def __init__(self, acc_dict: Dict):
        self.status = acc_dict.get('account_status', acc_dict.get('status', 'current'))
        self.type = acc_dict.get('account_type', acc_dict.get('type', 'other'))
        self.balance = float(acc_dict.get('balance', 0))
        self.limit = acc_dict.get('credit_limit', acc_dict.get('limit', None))
        if self.limit:
            self.limit = float(self.limit)
        
        # Convert months_open to open_date (approximate)
        months_open = acc_dict.get('months_open', 0)
        self.open_date = (datetime.now() - timedelta(days=int(months_open * 30.44))).date()
        
        # Optional attributes
        self.name = acc_dict.get('issuer', '')
        self.id = acc_dict.get('id', None)


class DictDerogatory:
    """Adapter to make dict derogatories compatible with ORM-based subscores functions."""
    def __init__(self, derog_dict: Dict):
        self.type = derog_dict.get('type', 'unknown')
        
        # Parse date string if needed
        date_val = derog_dict.get('date', datetime.now())
        if isinstance(date_val, str):
            try:
                self.date = datetime.fromisoformat(date_val).date()
            except:
                self.date = datetime.now().date()
        else:
            self.date = date_val if hasattr(date_val, 'date') else date_val.date() if hasattr(date_val, 'date') else datetime.now().date()
        
        self.details = derog_dict.get('details', '')


class FicoEngine:
    """
    FICO Score Calculator Engine (Orchestrator)
    
    Four-layer architecture mirrors real FICO scoring:
      Layer 1: Extract features from raw profile
      Layer 2: Segment profile into scorecard
      Layer 3: Calculate subscores (5 factors)
      Layer 4: Aggregate subscores → FICO score
    
    Score range: 300-850
    """
    
    MIN_SCORE = 300
    MAX_SCORE = 850
    DEFAULT_MODEL = "linear"
    
    def __init__(self, model: str = None):
        """Create engine instance. Pass `model='fico8'` to use bucketed model."""
        self.model_name = model or self.DEFAULT_MODEL

    def calculate_full_score(self, credit_profile: Union[Dict, Any]) -> Dict[str, Any]:
        """
        Calculate complete FICO score using 4-layer architecture.
        
        Args:
            credit_profile: CreditProfile object or dict with 'accounts'/'derogatories'
            
        Returns:
            Dict with score, subscores, scorecard, and details
        """
        
        # Convert to dict if needed (support both ORM objects and dicts)
        profile_dict = self._to_dict(credit_profile)
        
        # LAYER 1: Extract Features
        features = extract_features(profile_dict)
        
        # LAYER 2: Determine Scorecard
        scorecard = determine_scorecard(profile_dict, features)
        
        # LAYER 3: Calculate Subscores (0-100)
        subscores = self._calculate_subscores(credit_profile, features)
        
        # LAYER 4: Aggregate Score
        # If a named model is requested (e.g., 'fico8'), attempt to use its
        # aggregation routine. Otherwise fall back to default linear aggregator.
        final_score = None
        if self.model_name and self.model_name.lower() == 'fico8':
            try:
                from .models import fico8 as fico8_model

                final_score = fico8_model.aggregate_score(subscores, scorecard)
            except Exception:
                # If model import or execution fails, fall back to default
                final_score = aggregate_score(subscores, scorecard)
        else:
            final_score = aggregate_score(subscores, scorecard)
        
        return {
            'score': final_score,
            'payment_history': int(round(subscores.get('payment_history', 50))),
            'utilization': int(round(subscores.get('utilization', 50))),
            'age': int(round(subscores.get('age', 50))),
            'new_credit': int(round(subscores.get('new_credit', 50))),
            'mix': int(round(subscores.get('mix', 50))),
            'scorecard': scorecard,
            'scorecard_description': get_scorecard_description(scorecard),
        }
    
    def calculate_score(self, credit_profile: Union[Dict, Any]) -> int:
        """Get just the final FICO score."""
        return self.calculate_full_score(credit_profile)['score']
    
    def _calculate_subscores(
        self,
        credit_profile: Any,
        features: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate factor subscores (0-100).
        
        Supports both ORM CreditProfile objects and dicts.
        """
        
        # Extract accounts/derogatories - support both dict and ORM object
        if isinstance(credit_profile, dict):
            accounts_raw = credit_profile.get('accounts', [])
            derogatories_raw = credit_profile.get('derogatories', [])
            # Normalize dict accounts to DictAccount objects (compatible with subscores functions)
            accounts = [DictAccount(acc) if isinstance(acc, dict) else acc for acc in accounts_raw]
            derogatories = [DictDerogatory(d) if isinstance(d, dict) else d for d in derogatories_raw]
        else:
            accounts = getattr(credit_profile, 'accounts', [])
            derogatories = getattr(credit_profile, 'derogatories', [])
        
        # Calculate subscores using existing functions
        payment_score = calculate_payment_history_score(accounts, derogatories)
        utilization_score = calculate_utilization_score(accounts)
        age_score = calculate_age_score(accounts)
        new_credit_score = calculate_new_credit_score(accounts)
        mix_score = calculate_mix_score(accounts)
        
        return {
            'payment_history': payment_score,
            'utilization': utilization_score,
            'age': age_score,
            'new_credit': new_credit_score,
            'mix': mix_score,
        }
    
    def _to_dict(self, profile: Any) -> Dict:
        """Convert CreditProfile ORM object to dict if needed."""
        if isinstance(profile, dict):
            return profile
        
        # ORM object
        accounts = []
        if hasattr(profile, 'accounts'):
            for acc in profile.accounts:
                accounts.append({
                    'id': getattr(acc, 'id', None),
                    'type': getattr(acc, 'type', 'other'),
                    'name': getattr(acc, 'name', ''),
                    'balance': float(getattr(acc, 'balance', 0)),
                    'limit': float(getattr(acc, 'limit', 0)) if getattr(acc, 'limit', None) else None,
                    'open_date': str(getattr(acc, 'open_date', '')),
                    'status': getattr(acc, 'status', 'active'),
                })
        
        derogatories = []
        if hasattr(profile, 'derogatories'):
            for d in profile.derogatories:
                derogatories.append({
                    'type': getattr(d, 'type', 'unknown'),
                    'date': str(getattr(d, 'date', '')),
                    'details': getattr(d, 'details', ''),
                })
        
        return {
            'accounts': accounts,
            'derogatories': derogatories,
        }
