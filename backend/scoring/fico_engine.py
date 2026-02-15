"""
FICO Score Calculator Engine - Orchestrator Pattern

Uses a 4-layer architecture:
  1. Feature Extraction Layer (normalize profiles)
  2. Scorecard Segmentation Layer (assign profile type)
  3. Factor Calculation Layer (subscores)
  4. Aggregation Layer (combine into final score)
"""

from typing import Dict, Any, Union
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
            accounts = credit_profile.get('accounts', [])
            derogatories = credit_profile.get('derogatories', [])
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
