import io
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from models import crud

client = TestClient(app)

def create_test_profile(db):
    user = crud.get_or_create_user(db, "test_export@example.com")
    profile = crud.create_credit_profile(db, user.id, "Export Test Profile")
    # Add dummy account and derogatory
    crud.create_account(db, profile.id, type="credit_card", name="Test Card", balance=123.45, limit=1000, open_date="2020-01-01", status="active")
    crud.create_derogatory(db, profile_id=profile.id, type="late_payment", date_val="2022-01-01", details="Missed payment")
    return profile

def test_export_profile_pdf(tmp_path):
    # Use DB session from app dependency
    from backend.main import get_db
    db = next(get_db())
    profile = create_test_profile(db)
    url = f"/profiles/{profile.id}/export/pdf"
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"].endswith(".pdf")
    # Save PDF to disk for manual inspection (optional)
    pdf_path = tmp_path / f"{profile.id}_report.pdf"
    pdf_path.write_bytes(response.content)
    assert pdf_path.stat().st_size > 1000  # Should be a non-trivial PDF file
