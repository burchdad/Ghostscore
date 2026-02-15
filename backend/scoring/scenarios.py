from typing import List, Dict
from copy import deepcopy

class ScenarioEngine:
    """
    Scenario simulator for testing credit improvement strategies
    """
    
    def __init__(self, fico_engine):
        self.engine = fico_engine
    
    def simulate_paydown(self, profile, account_id: str, new_balance: float):
        """
        Simulate score change from paying down a single account
        
        Args:
            profile: CreditProfile
            account_id: ID of account to modify
            new_balance: New balance after paydown
            
        Returns:
            dict with old score, new score, and delta
        """
        # Calculate original score
        original_result = self.engine.calculate_full_score(profile)
        original_score = original_result['score']
        
        # Create modified profile
        modified_profile = deepcopy(profile)
        
        # Find and update account
        for account in modified_profile.accounts:
            if account.id == account_id:
                account.balance = new_balance
                break
        
        # Calculate new score
        new_result = self.engine.calculate_full_score(modified_profile)
        new_score = new_result['score']
        
        return {
            'original_score': original_score,
            'original_subscores': original_result,
            'new_score': new_score,
            'new_subscores': new_result,
            'score_delta': new_score - original_score,
        }
    
    def simulate_payoff(self, profile, account_id: str):
        """
        Simulate score change from paying off an account completely
        """
        return self.simulate_paydown(profile, account_id, 0.0)
    
    def simulate_multiple_scenarios(self, profile, scenarios: List[dict]):
        """
        Simulate multiple paydown scenarios at once
        
        Each scenario in list should have: account_id and new_balance
        """
        results = []
        
        for scenario in scenarios:
            account_id = scenario.get('account_id')
            new_balance = scenario.get('new_balance', 0)
            
            result = self.simulate_paydown(profile, account_id, new_balance)
            result['scenario_name'] = scenario.get('name', f'Paydown to ${new_balance}')
            results.append(result)
        
        # Sort by score delta (descending) - best improvements first
        results.sort(key=lambda x: x['score_delta'], reverse=True)
        
        return results
    
    def get_recommendations(self, profile):
        """
        Generate smart recommendations for score improvement
        
        Analyzes profile and suggests:
        1. High-impact paydowns
        2. Account closure strategies
        3. Priority order
        """
        current_result = self.engine.calculate_full_score(profile)
        current_score = current_result['score']
        utilization = current_result['utilization']
        
        recommendations = []
        total_potential_gain = 0
        
        # Find credit cards with high utilization
        credit_cards = [acc for acc in profile.accounts 
                       if acc.type == "credit_card" and acc.limit]
        
        if credit_cards:
            for card in credit_cards:
                util_ratio = card.balance / card.limit if card.limit > 0 else 0
                
                # If card has high utilization, suggest paydown
                if util_ratio > 0.30:
                    # Calculate optimal paydown target (under 10% utilization)
                    target_balance = card.limit * 0.09
                    
                    if target_balance < card.balance:
                        scenario_result = self.simulate_paydown(profile, card.id, target_balance)
                        gain = scenario_result['score_delta']
                        
                        if gain > 0:
                            recommendations.append({
                                'action': 'paydown',
                                'account': card.name or card.id,
                                'current_balance': card.balance,
                                'target_balance': target_balance,
                                'amount_to_pay': card.balance - target_balance,
                                'score_gain': gain,
                                'priority': 'high' if util_ratio > 0.70 else 'medium',
                            })
                            total_potential_gain += gain
        
        # Check for derogatory marks that can't be removed but are aging
        if profile.derogatories:
            for derog in profile.derogatories:
                days_ago = 0
                from datetime import date as date_module
                days_ago = (date_module.today() - derog.date).days
                
                if days_ago < 365 * 7:  # Within 7 years
                    recommendations.append({
                        'action': 'wait',
                        'item': derog.type,
                        'date': str(derog.date),
                        'years_remaining': round((365 * 7 - days_ago) / 365, 1),
                        'note': f"{derog.type} will age off in {round((365 * 7 - days_ago) / 365, 1)} years",
                    })
        
        # Sort by priority and score gain
        recommendations.sort(
            key=lambda x: (
                {'high': 0, 'medium': 1, 'low': 2}.get(x.get('priority', 'low'), 3),
                -x.get('score_gain', 0)
            )
        )
        
        return {
            'current_score': current_score,
            'estimated_potential_gain': total_potential_gain,
            'recommendations': recommendations[:5],  # Top 5 recommendations
        }
