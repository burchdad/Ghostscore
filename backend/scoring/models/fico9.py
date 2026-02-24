class Fico9Model:
    def score(self, features):
        # FICO 9: paid collections ignored, medical collections penalized less, less aggressive utilization
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
