"""
Credit Karma JSON Parser for GhostScore

Converts raw Credit Karma JSON export into GhostScore's normalized profile schema.
Compatible with feature_engine.extract_features().
"""
import json
from typing import Any, Dict, List

def parse_creditkarma_json(raw_json: str) -> Dict[str, Any]:
    """
    Parse Credit Karma JSON export and return normalized profile dict.
    Args:
        raw_json: JSON string from Credit Karma export
    Returns:
        dict with keys: accounts, derogatories, inquiries, personal_info
    """
    data = json.loads(raw_json) if isinstance(raw_json, str) else raw_json

    # Example structure, adapt as needed for real CK export
    accounts = []
    derogatories = []
    inquiries = []
    personal_info = {}

    # Parse accounts
    for acct in data.get("accounts", []):
        accounts.append({
            "id": acct.get("id") or acct.get("accountNumber"),
            "type": acct.get("type"),
            "name": acct.get("name") or acct.get("lenderName"),
            "balance": acct.get("balance", 0),
            "limit": acct.get("creditLimit"),
            "open_date": acct.get("openedOn"),
            "status": acct.get("status"),
        })

    # Parse derogatories (late payments, collections, charge-offs)
    for acct in data.get("accounts", []):
        if acct.get("negativeIndicators"):
            for neg in acct["negativeIndicators"]:
                derogatories.append({
                    "id": acct.get("id") or acct.get("accountNumber"),
                    "type": neg.get("type"),
                    "date": neg.get("date"),
                    "details": neg.get("details"),
                })

    # Parse inquiries
    for inq in data.get("inquiries", []):
        inquiries.append({
            "date": inq.get("date"),
            "type": inq.get("type"),
            "lender": inq.get("lender"),
        })

    # Parse personal info
    pi = data.get("personalInfo", {})
    personal_info = {
        "name": pi.get("name"),
        "dob": pi.get("dob"),
        "ssn": pi.get("ssn"),
        "address": pi.get("address"),
    }

    return {
        "accounts": accounts,
        "derogatories": derogatories,
        "inquiries": inquiries,
        "personal_info": personal_info,
    }

# Example usage:
# with open("sample_creditkarma.json") as f:
#     profile = parse_creditkarma_json(f.read())
#     features = feature_engine.extract_features(profile)
