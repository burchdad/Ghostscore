class ExplainEngine:
    def explain_score(self, profile, subscores):
        explanations = []
        if hasattr(subscores, 'utilization') and subscores.utilization < 70:
            explanations.append({
                "factor": "utilization",
                "impact": "negative",
                "reason": "High credit utilization"
            })
        if hasattr(subscores, 'payment_history') and subscores.payment_history > 95:
            explanations.append({
                "factor": "payment_history",
                "impact": "positive",
                "reason": "Strong on-time payment history"
            })
        return explanations
