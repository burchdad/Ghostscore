"""
Test for Credit Karma JSON parser
"""
import json
from creditkarma_json import parse_creditkarma_json

def test_parse_creditkarma_json():
    # Minimal sample CK JSON
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
    assert profile["accounts"][0]["name"] == "Chase Sapphire"
    assert profile["accounts"][0]["limit"] == 5000
    assert profile["derogatories"][0]["type"] == "late_payment"
    assert profile["inquiries"][0]["lender"] == "Amex"
    assert profile["personal_info"]["name"] == "Jane Doe"
    print("All assertions passed.")

if __name__ == "__main__":
    test_parse_creditkarma_json()
