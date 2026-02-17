"""
Example: Parse Credit Karma JSON and extract features
"""
import json
from creditkarma_json import parse_creditkarma_json
from ..scoring import feature_engine

def main():
    # Example sample CK JSON
    sample = {
        "accounts": [
            {
                "id": "acc1",
                "type": "credit_card",
                "name": "Chase Sapphire",
                "balance": 1200,
                "creditLimit": 5000,
                "openedOn": "2020-01-01",
                "status": "active",
                "negativeIndicators": [
                    {"type": "late_payment", "date": "2023-01-15", "details": "30 days late"}
                ]
            }
        ],
        "inquiries": [
            {"date": "2024-01-01", "type": "hard", "lender": "Amex"}
        ],
        "personalInfo": {
            "name": "Jane Doe",
            "dob": "1990-05-10",
            "ssn": "123-45-6789",
            "address": "123 Main St, Anytown, USA"
        }
    }
    profile = parse_creditkarma_json(sample)
    features = feature_engine.extract_features(profile)
    print("Extracted features:", features)

if __name__ == "__main__":
    main()
