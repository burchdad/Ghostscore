from datetime import datetime, date
from typing import List, Dict
from .subscores import (
    calculate_payment_history_score,
    calculate_utilization_score,
    calculate_age_score,
    calculate_new_credit_score,
    calculate_mix_score
)

class FicoEngine:
    """
    FICO Score Calculator Engine
    
    Weights:
    - Payment History: 35% (35 points)
    - Credit Utilization: 30% (30 points)
    - Age of Credit: 15% (15 points)
    - New Credit: 10% (10 points)
    - Credit Mix: 10% (10 points)
    
    Score range: 300-850
    """
    
    # Weights for each factor
    WEIGHTS = {
        'payment_history': 0.35,
        'utilization': 0.30,
        'age': 0.15,
        'new_credit': 0.10,
        'mix': 0.10,
    }
    
    MIN_SCORE = 300
    MAX_SCORE = 850
    
    def calculate_full_score(self, credit_profile):
        """
        Calculate complete FICO score and all subscores
        
        Args:
            credit_profile: CreditProfile object with accounts and derogatories
            
        Returns:
            dict with main score and all subscores
        """
        # Calculate subscores (0-100)
        payment_score = calculate_payment_history_score(
            credit_profile.accounts,
            credit_profile.derogatories
        )
        utilization_score = calculate_utilization_score(credit_profile.accounts)
        age_score = calculate_age_score(credit_profile.accounts)
        new_credit_score = calculate_new_credit_score(credit_profile.accounts)
        mix_score = calculate_mix_score(credit_profile.accounts)
        
        # Convert subscores (0-100) to contribution points
        # Start with base 300, scale each subscore by weight and range
        score = (
            self.MIN_SCORE +
            (payment_score * 100 * self.WEIGHTS['payment_history']) +
            (utilization_score * 100 * self.WEIGHTS['utilization']) +
            (age_score * 100 * self.WEIGHTS['age']) +
            (new_credit_score * 100 * self.WEIGHTS['new_credit']) +
            (mix_score * 100 * self.WEIGHTS['mix'])
        )
        
        # Clamp to valid range
        final_score = min(max(int(round(score)), self.MIN_SCORE), self.MAX_SCORE)
        
        return {
            'score': final_score,
            'payment_history': int(round(payment_score)),
            'utilization': int(round(utilization_score)),
            'age': int(round(age_score)),
            'new_credit': int(round(new_credit_score)),
            'mix': int(round(mix_score)),
        }
    
    def calculate_score(self, credit_profile):
        """Quick method to get just the score"""
        return self.calculate_full_score(credit_profile)['score']
