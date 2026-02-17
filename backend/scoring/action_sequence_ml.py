
"""
ML-Based Action Sequencing Pipeline (Real Model Wrapper)
"""
from typing import List, Dict, Any
from .action_sequence_ml_model import ml_action_sequencer

def fit_action_sequence_model(user_histories: List[Dict[str, Any]]):
    """
    Fit the ML model on user scenario histories.
    """
    ml_action_sequencer.fit(user_histories)

def predict_optimal_sequence(features: Dict[str, Any], max_len: int = 5) -> List[int]:
    """
    Predict the optimal action sequence for given features.
    """
    return ml_action_sequencer.predict_sequence(features, max_len=max_len)
