import tempfile
from pathlib import Path
from utils.credit_report_parser import parse_credit_report, Bureau


def test_parse_txt_report_basic():
    content = """
Creditor: Chase Sapphire Preferred
Type: Credit Card
Current Balance: $2,500
Credit Limit: $5,000
Date Opened: 01/15/2020
Status: Current

Creditor: Car Loan
Type: Auto Loan
Current Balance: $15,000
Date Opened: 03/10/2021
Status: Current
"""
    # use sample file instead of creating inline
    from pathlib import Path
    sample = Path(__file__).parent / 'samples' / 'sample_equifax.txt'
    accounts, status = parse_credit_report(str(sample), Bureau.EQUIFAX)
    assert isinstance(accounts, list)
    assert len(accounts) >= 2
    names = [a.get('name', '').lower() for a in accounts]
    assert any('chase' in n for n in names)
    assert any('car' in n or 'loan' in n for n in names)


def test_parse_csv_report_basic():
    from pathlib import Path
    sample = Path(__file__).parent / 'samples' / 'sample_experian.csv'
    accounts, status = parse_credit_report(str(sample), Bureau.EXPERIAN)
    assert isinstance(accounts, list)
    assert len(accounts) == 2
    assert any('chase' in a.get('name', '').lower() for a in accounts)
    
