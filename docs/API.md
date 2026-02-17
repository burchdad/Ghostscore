# GhostScore API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication (Phase 1 MVP).

## Health Check

**Get API Status**
```
GET /health

Response: 200 OK
{
  "status": "ok",
  "service": "GhostScore API"
}
```


## Credit Score Endpoints
---

### Calibrate Profile

**Run calibration for a profile to improve score accuracy using real credit report data.**

```
POST /profiles/{profile_id}/calibrate
Content-Type: application/json

Response: 200 OK
{
  "message": "Calibration complete! Correction factors updated."
}
```

**Errors:**
- 404 Not Found: Profile not found
- 500 Server Error: Calibration failed

---

### Optimize Credit Profile (Goal-Based)

**Find optimal strategy to reach a target score or constraint.**

```
POST /optimize/goal
Content-Type: application/json

Body:
{
  "accounts": [...],
  "derogatories": [],
  "goal": {
    "target_score": 700,
    "max_monthly_payment": 500
  }
}

Response: 200 OK
{
  "current_score": 650,
  "recommended_actions": [ ... ],
  "estimated_timeline": [ ... ],
  "total_potential_gain": 50
}
```

---

### Upload Credit Bureau Report

**Upload a credit report file (PDF or TXT) for extraction.**

```
POST /profiles/{profile_id}/upload-credit-report
Content-Type: multipart/form-data

Form Data:
- file: (PDF or TXT file)
- bureau: equifax | experian | transunion

Response: 200 OK
{
  "status": "Extracted 5 accounts from Equifax report.",
  "accounts": [ ... ]
}
```

---

### Import Accounts from Extracted Report

**Import selected accounts after extraction.**

```
POST /profiles/{profile_id}/import-accounts-from-report
Content-Type: application/json

Body:
{
  "accounts": [ ... ],
  "selected_indices": [0, 2, 3]
}

Response: 200 OK
{
  "imported_count": 3,
  "accounts": [ ... ]
}
```

### Calculate FICO Score

**Calculate full FICO score with all subscores**

```
POST /score
Content-Type: application/json

Body:
{
  "accounts": [
    {
      "id": "cc_1",
      "type": "credit_card",
      "name": "Chase Sapphire Preferred",
      "balance": 2500,
      "limit": 5000,
      "open_date": "2020-01-15",
      "status": "active"
    },
    {
      "id": "loan_1",
      "type": "personal_loan",
      "name": "SoFi Personal Loan",
      "balance": 5000,
      "open_date": "2021-06-20",
      "status": "active"
    }
  ],
  "derogatories": []
}

Response: 200 OK
{
  "score": 655,
  "payment_history": 78,
  "utilization": 68,
  "age": 65,
  "new_credit": 78,
  "mix": 75
}
```

**Errors:**
- 400 Bad Request: Invalid profile data

---

### Simulate Paydown

**Simulate score impact of paying down an account**

```
POST /simulate/paydown
Content-Type: application/json

Body:
{
  "profile": {
    "accounts": [...],
    "derogatories": []
  },
  "account_id": "cc_1",
  "new_balance": 1250
}

Response: 200 OK
{
  "original_score": 655,
  "original_subscores": {
    "score": 655,
    "payment_history": 78,
    "utilization": 68,
    "age": 65,
    "new_credit": 78,
    "mix": 75
  },
  "new_score": 673,
  "new_subscores": {
    "score": 673,
    "payment_history": 78,
    "utilization": 85,
    "age": 65,
    "new_credit": 78,
    "mix": 75
  },
  "score_delta": 18
}
```

---

### Simulate Multiple Scenarios

**Compare multiple paydown scenarios**

```
POST /simulate/multiple
Content-Type: application/json

Body:
{
  "profile": {...},
  "scenarios": [
    {
      "name": "Pay down Card A to $500",
      "account_id": "cc_1",
      "new_balance": 500
    },
    {
      "name": "Pay off Card B completely",
      "account_id": "cc_2",
      "new_balance": 0
    }
  ]
}

Response: 200 OK
{
  "scenarios": [
    {
      "scenario_name": "Pay off Card B completely",
      "original_score": 655,
      "new_score": 690,
      "score_delta": 35
    },
    {
      "scenario_name": "Pay down Card A to $500",
      "original_score": 655,
      "new_score": 673,
      "score_delta": 18
    }
  ]
}
```

---

### Get Recommendations

**Get smart optimization recommendations**

```
POST /recommendations
Content-Type: application/json

Body:
{
  "accounts": [...],
  "derogatories": []
}

Response: 200 OK
{
  "current_score": 655,
  "estimated_potential_gain": 87,
  "recommendations": [
    {
      "action": "paydown",
      "account": "Chase Sapphire Preferred",
      "current_balance": 2500,
      "target_balance": 450,
      "amount_to_pay": 2050,
      "score_gain": 35,
      "priority": "high"
    },
    {
      "action": "paydown",
      "account": "Amex Blue",
      "current_balance": 1200,
      "target_balance": 90,
      "amount_to_pay": 1110,
      "score_gain": 18,
      "priority": "medium"
    },
    {
      "action": "wait",
      "item": "late_payment",
      "date": "2022-05-15",
      "years_remaining": 5.8,
      "note": "late_payment will age off in 5.8 years"
    }
  ]
}
```

---

## Data Models

### Account

```typescript
{
  id: string              // Unique identifier
  type: string            // credit_card, loan, mortgage, auto_loan, student_loan
  name: string            // User-friendly name (e.g., "Chase Sapphire")
  balance: number         // Current balance
  limit: number | null    // Credit limit (null for loans)
  open_date: string       // Date account opened (YYYY-MM-DD)
  status: string          // active, closed, charged_off
}
```

### Derogatory

```typescript
{
  id: string              // Unique identifier
  type: string            // late_payment, collection, charge_off, bankruptcy
  date: string            // Date of derogatory (YYYY-MM-DD)
  details: string | null  // Optional details
}
```

### Credit Profile

```typescript
{
  id?: string             // Optional profile ID
  user_id?: string        // Optional user ID
  accounts: Account[]
  derogatories: Derogatory[]
}
```

### Score Response

```typescript
{
  score: number           // 300-850
  payment_history: number // 0-100
  utilization: number     // 0-100
  age: number             // 0-100
  new_credit: number      // 0-100
  mix: number             // 0-100
}
```

---

## Error Responses

All errors return JSON with status code and message:

```json
{
  "detail": "Error description"
}
```

**Common Status Codes:**
- 200: Success
- 400: Bad Request (invalid data)
- 404: Not Found
- 500: Server Error

---

## Example Usage with Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Create profile
profile = {
    "accounts": [
        {
            "id": "card1",
            "type": "credit_card",
            "name": "Chase Sapphire",
            "balance": 2500,
            "limit": 5000,
            "open_date": "2020-01-15",
            "status": "active"
        }
    ],
    "derogatories": []
}

# Calculate score
response = requests.post(f"{BASE_URL}/score", json=profile)
score = response.json()
print(f"Your FICO Score: {score['score']}")
print(f"Utilization Score: {score['utilization']}")

# Simulate paydown
simulation = {
    "profile": profile,
    "account_id": "card1",
    "new_balance": 1250
}
response = requests.post(f"{BASE_URL}/simulate/paydown", json=simulation)
result = response.json()
print(f"Potential score increase: +{result['score_delta']} points")

# Get recommendations
response = requests.post(f"{BASE_URL}/recommendations", json=profile)
recs = response.json()
print(f"Potential gain: +{recs['estimated_potential_gain']} points")
```

---

## Rate Limits

Currently unlimited for MVP. Future versions will implement rate limiting.

---

## Support

For issues or questions, contact Ghost AI Solutions.
