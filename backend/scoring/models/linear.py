class LinearModel:
    def score(self, features):
        # Simple linear model for demonstration
        return int(
            0.35 * features.get('payment_history', 0) +
            0.30 * features.get('utilization', 0) +
            0.15 * features.get('age', 0) +
            0.10 * features.get('new_credit', 0) +
            0.10 * features.get('mix', 0)
        )
