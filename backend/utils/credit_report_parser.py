"""
Credit report parser for Equifax, Experian, and Transunion reports.
Extracts account information from uploaded credit reports.
"""

import re
import csv
import os
from typing import Any
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
from enum import Enum


class Bureau(str, Enum):
    EQUIFAX = "equifax"
    EXPERIAN = "experian"
    TRANSUNION = "transunion"


class AccountExtractor:
    """Base class for extracting accounts from credit report text"""
    
    # Account type mappings
    ACCOUNT_TYPE_MAPPING = {
        'credit card': 'credit_card',
        'credit line': 'credit_card',
        'auto loan': 'auto_loan',
        'auto': 'auto_loan',
        'car loan': 'auto_loan',
        'mortgage': 'mortgage',
        'home loan': 'mortgage',
        'student loan': 'student_loan',
        'personal loan': 'personal_loan',
        'installment': 'installment_loan',
        'medical': 'other',
        'charge card': 'charge_card',
    }
    
    # Status mappings
    STATUS_MAPPING = {
        'active': 'active',
        'open': 'active',
        'current': 'active',
        'closed': 'closed',
        'paid off': 'closed',
        'charged off': 'charged_off',
        'delinquent': 'delinquent',
        '30 days': 'delinquent',
        '60 days': 'delinquent',
        '90 days': 'delinquent',
        '120 days': 'delinquent',
        'collections': 'collections',
        'paid in full': 'closed',
    }
    
    def __init__(self, text: str):
        self.text = text.lower()
        self.lines = text.split('\n')
    
    def normalize_account_type(self, account_type: str) -> str:
        """Normalize account type to standard format"""
        account_type_lower = account_type.lower().strip()
        for key, value in self.ACCOUNT_TYPE_MAPPING.items():
            if key in account_type_lower:
                return value
        return 'other'
    
    def normalize_status(self, status: str) -> str:
        """Normalize account status to standard format"""
        status_lower = status.lower().strip()
        for key, value in self.STATUS_MAPPING.items():
            if key in status_lower:
                return value
        return 'active'
    
    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse various date formats to YYYY-MM-DD"""
        if not date_str or not date_str.strip():
            return None
        
        date_str = date_str.strip()
        
        # Try common formats
        formats = [
            '%m/%d/%Y',
            '%m/%d/%y',
            '%m-%d-%Y',
            '%m-%d-%y',
            '%B %d, %Y',
            '%b %d, %Y',
            '%Y-%m-%d',
            '%d/%m/%Y',
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def parse_currency(self, value_str: str) -> Optional[float]:
        """Parse currency string to float"""
        if not value_str or not value_str.strip():
            return None
        
        # Remove common currency symbols and letters
        value_str = re.sub(r'[$,\s]', '', value_str.strip())
        
        # Remove non-numeric except decimal point
        value_str = re.sub(r'[^\d.]', '', value_str)
        
        try:
            return float(value_str)
        except ValueError:
            return None
    
    def extract_accounts(self) -> List[Dict]:
        """Extract accounts from credit report text. Override in subclass."""
        raise NotImplementedError

    def run_additional_heuristics(self) -> List[Dict]:
        """Fallback heuristics to find creditor blocks like 'Creditor: NAME' and nearby balances."""
        accounts = []
        lines = self.lines
        for i, line in enumerate(lines):
            m = re.search(r'creditor\s*[:\-]\s*(.+)', line, re.IGNORECASE)
            if m:
                name = m.group(1).strip()
                balance = None
                limit = None
                open_date = None
                status = 'active'
                # look ahead next few lines for fields
                for j in range(i, min(i + 6, len(lines))):
                    l = lines[j]
                    mb = re.search(r'(current balance|balance|amount owed)\s*[:\-]?\s*\$?([\d,\.]+)', l, re.IGNORECASE)
                    if mb:
                        try:
                            balance = float(mb.group(2).replace(',', ''))
                        except Exception:
                            balance = None
                    ml = re.search(r'(credit limit|limit|high credit)\s*[:\-]?\s*\$?([\d,\.]+)', l, re.IGNORECASE)
                    if ml:
                        try:
                            limit = float(ml.group(2).replace(',', ''))
                        except Exception:
                            limit = None
                    mo = re.search(r'(opened|date opened|since)\s*[:\-]?\s*(.+)', l, re.IGNORECASE)
                    if mo:
                        parsed = self.parse_date(mo.group(2))
                        if parsed:
                            open_date = parsed
                    ms = re.search(r'(status|account status)\s*[:\-]?\s*(.+)', l, re.IGNORECASE)
                    if ms:
                        status = self.normalize_status(ms.group(2))

                accounts.append({
                    'name': name,
                    'type': 'other',
                    'balance': balance or 0.0,
                    'limit': limit,
                    'open_date': open_date or date.today().isoformat(),
                    'status': status,
                })
        return accounts

    def parse_compact_line(self, line: str) -> Optional[Dict]:
        """Parse lines like 'Chase Sapphire - Current Balance: $2,500 - Opened: 01/15/2020'"""
        # try to extract name before a dash and a balance token
        m = re.search(r'^(?P<name>[^-\n]+)\s[-–—]\s.*?(balance|current balance)[:\s]*\$?(?P<bal>[\d,\.]+)', line, re.IGNORECASE)
        if m:
            name = m.group('name').strip()
            bal = m.group('bal')
            try:
                balance = float(bal.replace(',', ''))
            except Exception:
                balance = 0.0
            # try to find opened date
            od = None
            mo = re.search(r'(opened|date opened|since|opened:)\s*[:\-]?\s*(?P<d>[0-9/\-]{6,20})', line, re.IGNORECASE)
            if mo:
                od = self.parse_date(mo.group('d'))
            return {
                'name': name,
                'type': 'other',
                'balance': balance,
                'limit': None,
                'open_date': od or date.today().isoformat(),
                'status': 'active',
            }
        return None


class EquifaxExtractor(AccountExtractor):
    """Extract accounts from Equifax credit report"""
    
    def extract_accounts(self) -> List[Dict]:
        """Extract accounts from Equifax format"""
        accounts = []
        
        # Equifax format typically has "TRADELINE" or account blocks
        # Pattern varies, so we look for common indicators
        
        lines = self.lines
        current_account = {}
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Look for account identifiers
            if re.search(r'(creditor|account|tradeline)', line_stripped, re.IGNORECASE):
                if current_account and 'name' in current_account:
                    accounts.append(current_account)
                current_account = {}
            
            # Extract account name
            if re.search(r'(creditor|account)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE):
                match = re.search(r'(creditor|account)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE)
                if match:
                    current_account['name'] = match.group(2).strip()
            
            # Extract account type
            if re.search(r'type\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE):
                match = re.search(r'type\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE)
                if match:
                    current_account['type'] = self.normalize_account_type(match.group(1))
            
            # Extract balance
            if re.search(r'(balance|amount owed|current balance)\s*[:\-]?\s*([\d,$.]+)', line_stripped, re.IGNORECASE):
                match = re.search(r'(balance|amount owed|current balance)\s*[:\-]?\s*([\d,$.]+)', line_stripped, re.IGNORECASE)
                if match:
                    balance = self.parse_currency(match.group(2))
                    if balance is not None:
                        current_account['balance'] = balance
            
            # Extract limit
            if re.search(r'(credit limit|limit|high credit)\s*[:\-]?\s*([\d,$.]+)', line_stripped, re.IGNORECASE):
                match = re.search(r'(credit limit|limit|high credit)\s*[:\-]?\s*([\d,$.]+)', line_stripped, re.IGNORECASE)
                if match:
                    limit = self.parse_currency(match.group(2))
                    if limit is not None:
                        current_account['limit'] = limit
            
            # Extract status
            if re.search(r'(status|account status)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE):
                match = re.search(r'(status|account status)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE)
                if match:
                    current_account['status'] = self.normalize_status(match.group(2))
            
            # Extract open date
            if re.search(r'(open|opened|date opened)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE):
                match = re.search(r'(open|opened|date opened)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE)
                if match:
                    parsed_date = self.parse_date(match.group(2))
                    if parsed_date:
                        current_account['open_date'] = parsed_date
        
        # Add last account
        if current_account and 'name' in current_account:
            accounts.append(current_account)
        
        return self._validate_accounts(accounts)
    
    def _validate_accounts(self, accounts: List[Dict]) -> List[Dict]:
        """Validate and clean extracted accounts"""
        validated = []
        
        for account in accounts:
            if 'name' not in account or not account['name']:
                continue
            
            # Set defaults
            if 'type' not in account:
                account['type'] = 'other'
            if 'balance' not in account:
                account['balance'] = 0.0
            if 'open_date' not in account:
                account['open_date'] = date.today().strftime('%Y-%m-%d')
            if 'status' not in account:
                account['status'] = 'active'
            
            validated.append(account)
        
        return validated


class ExperianExtractor(AccountExtractor):
    """Extract accounts from Experian credit report"""
    
    def extract_accounts(self) -> List[Dict]:
        """Extract accounts from Experian format"""
        accounts = []
        
        # Experian format often uses "ACCOUNTS" or "CREDIT ACCOUNTS" section
        lines = self.lines
        current_account = {}
        in_accounts_section = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Look for accounts section
            if 'accounts' in line_stripped.lower():
                in_accounts_section = True
                continue
            
            if not in_accounts_section:
                continue
            
            # Account separator
            if re.search(r'^[\-=]+$', line_stripped):
                if current_account and 'name' in current_account:
                    accounts.append(current_account)
                current_account = {}
                continue
            
            # Account name (usually at start of block)
            if line_stripped and not any(x in line_stripped.lower() for x in [':', '-']):
                if current_account and 'name' in current_account:
                    current_account['name'] = line_stripped
                elif not current_account:
                    current_account['name'] = line_stripped
            
            # Extract account type
            if re.search(r'type\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE):
                match = re.search(r'type\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE)
                if match:
                    current_account['type'] = self.normalize_account_type(match.group(1))
            
            # Extract balance
            if re.search(r'(current balance|balance|amount owed)\s*[:\-]?\s*([\d,$.]+)', line_stripped, re.IGNORECASE):
                match = re.search(r'(current balance|balance|amount owed)\s*[:\-]?\s*([\d,$.]+)', line_stripped, re.IGNORECASE)
                if match:
                    balance = self.parse_currency(match.group(2))
                    if balance is not None:
                        current_account['balance'] = balance
            
            # Extract limit/high credit
            if re.search(r'(credit limit|limit|$|high credit)\s*[:\-]?\s*([\d,$.]+)', line_stripped, re.IGNORECASE):
                match = re.search(r'(credit limit|limit|high credit)\s*[:\-]?\s*([\d,$.]+)', line_stripped, re.IGNORECASE)
                if match and '$' not in match.group(0)[:5]:  # Avoid matching currency in descriptions
                    limit = self.parse_currency(match.group(2))
                    if limit is not None and limit > 0:
                        current_account['limit'] = limit
            
            # Extract status
            if re.search(r'(status|account status)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE):
                match = re.search(r'(status|account status)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE)
                if match:
                    current_account['status'] = self.normalize_status(match.group(2))
            
            # Extract date opened
            if re.search(r'(opened|date opened|since)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE):
                match = re.search(r'(opened|date opened|since)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE)
                if match:
                    parsed_date = self.parse_date(match.group(2))
                    if parsed_date:
                        current_account['open_date'] = parsed_date
        
        if current_account and 'name' in current_account:
            accounts.append(current_account)
        
        return self._validate_accounts(accounts)
    
    def _validate_accounts(self, accounts: List[Dict]) -> List[Dict]:
        """Validate and clean extracted accounts"""
        validated = []
        
        for account in accounts:
            if 'name' not in account or not account['name']:
                continue
            
            # Set defaults
            if 'type' not in account:
                account['type'] = 'other'
            if 'balance' not in account:
                account['balance'] = 0.0
            if 'open_date' not in account:
                account['open_date'] = date.today().strftime('%Y-%m-%d')
            if 'status' not in account:
                account['status'] = 'active'
            
            validated.append(account)
        
        return validated


class TransunionExtractor(AccountExtractor):
    """Extract accounts from Transunion credit report"""
    
    def extract_accounts(self) -> List[Dict]:
        """Extract accounts from Transunion format"""
        accounts = []
        
        # Transunion format often has clear account blocks
        lines = self.lines
        current_account = {}
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Look for account number or creditor name
            if re.search(r'(creditor|account|company)\s*[:\-]', line_stripped, re.IGNORECASE):
                if current_account and 'name' in current_account:
                    accounts.append(current_account)
                current_account = {}
                
                match = re.search(r'(creditor|account|company)\s*[:\-]\s*(.+)', line_stripped, re.IGNORECASE)
                if match:
                    current_account['name'] = match.group(2).strip()
            
            # Extract account type
            if re.search(r'(type|account type)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE):
                match = re.search(r'(type|account type)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE)
                if match:
                    current_account['type'] = self.normalize_account_type(match.group(2))
            
            # Extract balance
            if re.search(r'(balance|account balance|current balance)\s*[:\-]?\s*([\d,$.]+)', line_stripped, re.IGNORECASE):
                match = re.search(r'(balance|account balance|current balance)\s*[:\-]?\s*([\d,$.]+)', line_stripped, re.IGNORECASE)
                if match:
                    balance = self.parse_currency(match.group(2))
                    if balance is not None:
                        current_account['balance'] = balance
            
            # Extract limit
            if re.search(r'(credit limit|$|high credit|max)\s*[:\-]?\s*([\d,$.]+)', line_stripped, re.IGNORECASE):
                match = re.search(r'(credit limit|high credit|max)\s*[:\-]?\s*([\d,$.]+)', line_stripped, re.IGNORECASE)
                if match:
                    limit = self.parse_currency(match.group(2))
                    if limit is not None and limit > 0:
                        current_account['limit'] = limit
            
            # Extract status
            if re.search(r'(status|condition)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE):
                match = re.search(r'(status|condition)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE)
                if match:
                    current_account['status'] = self.normalize_status(match.group(2))
            
            # Extract date opened
            if re.search(r'(opened|date opened|opened date)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE):
                match = re.search(r'(opened|date opened|opened date)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE)
                if match:
                    parsed_date = self.parse_date(match.group(2))
                    if parsed_date:
                        current_account['open_date'] = parsed_date
        
        if current_account and 'name' in current_account:
            accounts.append(current_account)
        
        return self._validate_accounts(accounts)
    
    def _validate_accounts(self, accounts: List[Dict]) -> List[Dict]:
        """Validate and clean extracted accounts"""
        validated = []
        
        for account in accounts:
            if 'name' not in account or not account['name']:
                continue
            
            # Set defaults
            if 'type' not in account:
                account['type'] = 'other'
            if 'balance' not in account:
                account['balance'] = 0.0
            if 'open_date' not in account:
                account['open_date'] = date.today().strftime('%Y-%m-%d')
            if 'status' not in account:
                account['status'] = 'active'
            
            validated.append(account)
        
        return validated


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    try:
        import PyPDF2
        
        text = []
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        
        return '\n'.join(text)
    except ImportError:
        raise ImportError("PyPDF2 is required for PDF parsing. Install with: pip install PyPDF2")
    except Exception as e:
        raise Exception(f"Error extracting PDF: {str(e)}")


def extract_text_with_ocr(file_path: str) -> str:
    """Attempt OCR on the provided file (image or PDF). Requires pytesseract and Pillow.

    For PDFs, attempts to use pdf2image if available to convert pages to images.
    """
    try:
        from PIL import Image
        import pytesseract
    except Exception:
        raise ImportError("pytesseract and Pillow required for OCR. Install with: pip install pytesseract Pillow")

    text_pages = []

    # If PDF, try to convert pages to images (pdf2image optional)
    if file_path.lower().endswith('.pdf'):
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(file_path)
            for img in images:
                text_pages.append(pytesseract.image_to_string(img))
        except Exception:
            # fallback: try reading PDF as bytes and OCR whole file (may fail)
            try:
                img = Image.open(file_path)
                text_pages.append(pytesseract.image_to_string(img))
            except Exception:
                # give up silently and return empty
                return ''
    else:
        # Assume image
        try:
            img = Image.open(file_path)
            text_pages.append(pytesseract.image_to_string(img))
        except Exception:
            return ''

    return '\n'.join([p for p in text_pages if p])


def parse_csv_report(file_path: str) -> list[Dict[str, Any]]:
    """Parse CSV credit report exports. Tries to map common headers to account fields."""
    accounts = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            headers = [h.lower() for h in reader.fieldnames or []]
            # Common header mappings
            header_map = {
                'account': ['account', 'account name', 'creditor', 'company'],
                'type': ['type', 'account type'],
                'balance': ['balance', 'current balance', 'amount owed'],
                'limit': ['limit', 'credit limit', 'high credit'],
                'open_date': ['opened', 'date opened', 'open date'],
                'status': ['status', 'account status'],
            }

            for row in reader:
                acc = {}
                # map fields
                for key, possibles in header_map.items():
                    for p in possibles:
                        if p in headers:
                            acc[key] = row.get(p) or row.get(p.title()) or row.get(p.upper())
                            break
                # fallback attempt using heuristics
                if 'account' not in acc or not acc.get('account'):
                    # try first column
                    if reader.fieldnames:
                        acc['account'] = row.get(reader.fieldnames[0])
                # normalize keys to expected
                accounts.append({
                    'name': acc.get('account', 'Unknown'),
                    'type': acc.get('type', 'other'),
                    'balance': float(re.sub(r'[^\d.-]', '', str(acc.get('balance') or '0')) or 0),
                    'limit': float(re.sub(r'[^\d.-]', '', str(acc.get('limit') or '0')) or 0) if acc.get('limit') else None,
                    'open_date': acc.get('open_date') or date.today().isoformat(),
                    'status': acc.get('status') or 'active',
                })
    except Exception:
        return []
    return accounts


def parse_credit_report(file_path: str, bureau: Bureau) -> Tuple[List[Dict], str]:
    """
    Parse credit report and extract accounts.
    
    Args:
        file_path: Path to credit report file (PDF or TXT)
        bureau: Credit bureau (equifax, experian, or transunion)
    
    Returns:
        Tuple of (accounts list, extraction_status_message)
    """
    try:
        # CSV support
        if file_path.lower().endswith('.csv'):
            accounts = parse_csv_report(file_path)
            status = f"Extracted {len(accounts)} account(s) from CSV export"
            return accounts, status

        # Extract text from file (PDF or TXT)
        if file_path.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()

        # If no usable text, try OCR fallback
        if not text or len(text.strip()) < 120:
            try:
                ocr_text = extract_text_with_ocr(file_path)
                if ocr_text and len(ocr_text.strip()) > 50:
                    text = ocr_text
            except Exception:
                # OCR not available or failed - continue
                pass

        if not text or len(text.strip()) < 100:
            return [], "Could not extract sufficient text from file"
        
        # Select appropriate extractor
        if bureau == Bureau.EQUIFAX:
            extractor = EquifaxExtractor(text)
        elif bureau == Bureau.EXPERIAN:
            extractor = ExperianExtractor(text)
        elif bureau == Bureau.TRANSUNION:
            extractor = TransunionExtractor(text)
        else:
            return [], f"Unknown bureau: {bureau}"
        
        # Extract accounts using extractor heuristics
        accounts = extractor.extract_accounts()

        # Additional heuristic pass: use extractor's fallback heuristics to find creditor blocks
        if not accounts:
            accounts = extractor.run_additional_heuristics()
        
        status = f"Successfully extracted {len(accounts)} account(s) from {bureau.value} report"
        return accounts, status
    
    except Exception as e:
        return [], f"Error parsing report: {str(e)}"
