"""
FICO 9 Model v9.0.0 (Immutable)
This file is frozen. Never modify. Only create a new version file if needed.
"""
class Fico9Model_v9_0_0:
    version = "9.0.0"
    def score(self, features):
        score = (
            0.35 * features.get('payment_history', 0) +
            0.28 * features.get('utilization', 0) +
            0.15 * features.get('age', 0) +
            0.10 * features.get('new_credit', 0) +
            0.12 * features.get('mix', 0)
        )
        if features.get('has_collections', False) and not features.get('collection_paid', False):
            if features.get('collection_medical', False):
                score -= 10
            else:
                score -= 20
        return int(score)
