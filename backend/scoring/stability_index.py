"""
Score Stability Index Engine

Computes a stability metric indicating how robust/stable credit scores are.
Higher stability = lower variance across models or metrics = more confident prediction.
"""

from typing import Union, List, Dict, Any
import statistics


class ScoreStabilityIndex:
    """
    Compute stability index from score variance across models or metrics.
    
    Stability Index ranges from 0-100:
    - 0-30: Highly volatile (low confidence)
    - 30-60: Moderate volatility  
    - 60-100: Stable (high confidence)
    """

    def compute(self, scores: Union[List[float], Dict[str, Any]]) -> float:
        """
        Compute stability index.
        
        Args:
            scores: Either list of scores from different models,
                   or dict of utility metrics (balance, age, derogatories, etc.)
        
        Returns:
            Stability index (0-100)
        """
        if isinstance(scores, dict):
            # If dict, extract numeric values and compute variance
            values = []
            for key, val in scores.items():
                if isinstance(val, (int, float)):
                    # Normalize to 0-1 range for comparison
                    values.append(min(100, max(0, val)) / 100.0)
            
            if not values or len(values) < 2:
                return 0.0
            
            return self._compute_from_values(values)
        
        elif isinstance(scores, list):
            # Normalize scores to 0-1 range
            if not scores or len(scores) < 2:
                return 0.0
            
            normalized = [min(850, max(300, s)) / 850.0 for s in scores]
            return self._compute_from_values(normalized)
        
        else:
            return 0.0

    def _compute_from_values(self, values: List[float]) -> float:
        """
        Compute stability index from normalized values.
        
        Strategy:
        - Low variance = high stability  
        - High variance = low stability
        - Coefficient of variation is used to compare across scales
        """
        if len(values) < 2:
            return 0.0
        
        mean = statistics.mean(values)
        
        # Special case: all values identical = perfect stability
        if len(set(values)) == 1:
            return 100.0
        
        # Compute coefficient of variation (std dev / mean)
        # This normalizes variance to compare across different value ranges
        try:
            stdev = statistics.stdev(values)
            if mean == 0:
                cv = stdev * 100  # Avoid division by zero
            else:
                cv = stdev / mean
        except statistics.StatisticsError:
            return 0.0
        
        # Convert CV to 0-100 stability scale
        # CV of 0 = perfect stability (100)
        # CV > 0.5 = low stability (approaching 0)
        stability = max(0.0, min(100.0, 100.0 * (1.0 - cv)))
        
        return round(stability, 1)

    def compute_risk_level(self, stability_index: float) -> str:
        """
        Determine risk level based on stability index.
        
        Args:
            stability_index: Stability index (0-100)
        
        Returns:
            Risk level: 'LOW', 'MEDIUM', or 'HIGH'
        """
        if stability_index >= 70:
            return "LOW"
        elif stability_index >= 40:
            return "MEDIUM"
        else:
            return "HIGH"
