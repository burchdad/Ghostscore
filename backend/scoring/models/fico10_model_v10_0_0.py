"""
FICO 10 Model v10.0.0 (Immutable)
This file is frozen. Never modify. Only create a new version file if needed.
"""
class Fico10Model_v10_0_0:
    version = "10.0.0"
    def score(self, features):
        recent_util = features.get('recent_utilization', features.get('utilization', 0))
        older_util = features.get('older_utilization', features.get('utilization', 0))
        score = (
            0.35 * features.get('payment_history', 0) +
            0.28 * recent_util * 1.25 +
            0.12 * older_util * 0.75 +
            0.15 * features.get('age', 0) +
            0.10 * features.get('new_credit', 0) +
            0.10 * features.get('mix', 0)
        )
        if features.get('recent_delinquency', False):
            score -= 30
        return int(score)
