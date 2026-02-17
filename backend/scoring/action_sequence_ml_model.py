"""
ML-Based Action Sequencing Pipeline (Real Model)

This module implements a real ML pipeline for action sequencing using scikit-learn.
"""
from typing import List, Dict, Any
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'action_sequence_rf_model.pkl')

class ActionSequenceML:
    def __init__(self):
        self.model = None
        self.encoder = LabelEncoder()
        if os.path.exists(MODEL_PATH):
            self.load()

    def fit(self, user_histories: List[Dict[str, Any]]):
        # Example: user_histories = [{"features": {...}, "sequence": [0,1,2]}, ...]
        X = []
        y = []
        for hist in user_histories:
            features = hist["features"]
            seq = hist["sequence"]
            # Flatten features and sequence for supervised learning
            for idx, action in enumerate(seq):
                X.append(list(features.values()) + [idx])
                y.append(action)
        X = np.array(X)
        y = self.encoder.fit_transform(y)
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        self.save()

    def predict_sequence(self, features: Dict[str, Any], max_len: int = 5) -> List[int]:
        if self.model is None:
            return list(range(max_len))  # fallback
        seq = []
        for idx in range(max_len):
            x = np.array(list(features.values()) + [idx]).reshape(1, -1)
            pred = self.model.predict(x)
            action = self.encoder.inverse_transform(pred)[0]
            seq.append(int(action))
        return seq

    def save(self):
        joblib.dump((self.model, self.encoder), MODEL_PATH)

    def load(self):
        self.model, self.encoder = joblib.load(MODEL_PATH)

# Singleton instance
ml_action_sequencer = ActionSequenceML()

# Example usage:
# ml_action_sequencer.fit(user_histories)
# optimal_seq = ml_action_sequencer.predict_sequence(features)
