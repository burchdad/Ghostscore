import hashlib
import json

class ValidationEngine:
    def fingerprint_profile(self, profile: dict) -> str:
        normalized = json.dumps(profile, sort_keys=True)
        return hashlib.sha256(normalized.encode()).hexdigest()

    def verify_consistency(self, profile, scorer):
        score1 = scorer.score(profile)
        score2 = scorer.score(profile)
        if score1 != score2:
            raise Exception("Score inconsistency detected")
        return True
