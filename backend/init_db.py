#!/usr/bin/env python
"""
Initialize GhostScore database and optionally create sample data
Run: python init_db.py
"""

import os
from datetime import date
from models.database import init_db, SessionLocal
from models import crud


def create_sample_data():
    """Create sample family profile with test data"""
    db = SessionLocal()
    
    try:
        # Create user
        user = crud.get_or_create_user(db, "family@ghostscore.local")
        print(f"✓ Created user: {user.email}")
        
        # Create profile
        profile = crud.create_credit_profile(db, user.id, "Family Credit Profile")
        print(f"✓ Created profile: {profile.name} (ID: {profile.id})")
        
        # Add sample accounts
        accounts = [
            {
                "type": "credit_card",
                "name": "Chase Sapphire Preferred",
                "balance": 2500.00,
                "limit": 5000.00,
                "open_date": date(2020, 1, 15),
                "status": "active",
            },
            {
                "type": "credit_card",
                "name": "American Express Blue",
                "balance": 1200.00,
                "limit": 3000.00,
                "open_date": date(2019, 6, 20),
                "status": "active",
            },
            {
                "type": "auto_loan",
                "name": "Car Loan",
                "balance": 15000.00,
                "limit": None,
                "open_date": date(2021, 3, 10),
                "status": "active",
            },
        ]
        
        for acc in accounts:
            created = crud.create_account(
                db,
                profile_id=profile.id,
                **acc
            )
            print(f"  ✓ Added account: {created.name}")
        
        # Add sample derogatory (optional - comment out if you want perfect history)
        # derog = crud.create_derogatory(
        #     db,
        #     profile_id=profile.id,
        #     type="late_payment",
        #     date_val=date(2022, 5, 15),
        #     details="30-day late payment"
        # )
        # print(f"  ✓ Added derogatory: {derog.type}")
        
        print(f"\n✓ Sample data created!")
        print(f"  Profile ID: {profile.id}")
        print(f"  Email: {user.email}")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("🔧 Initializing GhostScore Database...")
    
    # Initialize database
    init_db()
    
    # Create sample data
    response = input("\nCreate sample family data? (y/N): ").strip().lower()
    if response == "y":
        create_sample_data()
    
    print("\n✅ Database ready!")
    print("Start the server with: uvicorn main:app --reload")
