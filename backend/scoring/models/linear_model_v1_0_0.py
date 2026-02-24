"""
Linear Model v1.0.0 (Immutable)
This file is frozen. Never modify. Only create a new version file if needed.
"""
class LinearModel_v1_0_0:
    version = "1.0.0"
    def score(self, features):
        return int(
            0.35 * features.get('payment_history', 0) +
            0.30 * features.get('utilization', 0) +
            0.15 * features.get('age', 0) +
            0.10 * features.get('new_credit', 0) +
            0.10 * features.get('mix', 0)
        )
