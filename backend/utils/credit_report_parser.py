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
    """Extract accounts from Equifax credit report using block-based structure"""
    
    def extract_accounts(self) -> List[Dict]:
        """
        Extract accounts from Equifax format using block segmentation.
        
        Equifax uses structured account blocks like:
        CREDITOR NAME - STATUS
        Balance: $XXX
        Account Number: *XXXX
        Loan Type: ...
        Date Opened: XX/XX/XXXX
        
        This parser splits on account headers and extracts fields from each block.
        """
        accounts = []
        text = self.text
        
        # Pattern to split account blocks
        # Matches: CREDITOR NAME - STATUS (at start of line or after whitespace)
        # where STATUS is "Closed", "Charge Off", "Collections", "Pays As Agreed", "Open", etc.
        account_header_pattern = r'\n([A-Z][A-Z0-9\s/,&.\-]*?(?:BANK|FINANCE|CREDIT|LLC|INC|CORPORATION|SERVICES|AUTO|CAPITAL|PREMIER|ONE|MANAGEMENT|CORP)?[A-Z0-9]*?)\s*[-–—]\s*(Closed|Charge\s+Off|Charged\s+Off|Open|Pays\s+As\s+Agreed|Current|30\s*Days?|60\s*Days?|90\s*Days?|120\s*Days?|Collections?|Collection\s+Account|Delinquent|Past\s+Due)'
        
        print(f"[EquifaxExtractor] Starting block-based extraction...")
        
        # Split text into blocks
        blocks = re.split(account_header_pattern, text)
        print(f"[EquifaxExtractor] Split text into {len(blocks)} segments (including separators)")
        
        # Process pairs of (creditor_name, status, block_text)
        i = 1
        block_count = 0
        while i < len(blocks) - 1:
            creditor_name = blocks[i].strip()
            status = blocks[i + 1].strip()
            
            # Skip empty names or if there's no block text
            if not creditor_name or len(creditor_name) < 3:
                print(f"[EquifaxExtractor] Skipping empty or short creditor name at block {i}")
                i += 3
                continue
            
            block_count += 1
            print(f"[EquifaxExtractor] Block {block_count}: {creditor_name} - {status}")
            
            # Get the text until the next account block or end
            if i + 3 < len(blocks):
                block_text = blocks[i + 2]
            else:
                block_text = text
            
            # Extract account from this block
            account = self._extract_from_block(creditor_name, status, block_text)
            if account:
                print(f"[EquifaxExtractor]   ✓ Extracted: {account['name']} | ${account.get('balance', 0)} | {account.get('status')}")
                accounts.append(account)
            else:
                print(f"[EquifaxExtractor]   ✗ Failed to extract account from block")
            
            i += 3
        
        print(f"[EquifaxExtractor] Block-based extraction found {len(accounts)} accounts")
        return accounts if accounts else self._fallback_extraction()
    
    def _extract_from_block(self, creditor_name: str, status_str: str, block_text: str) -> Optional[Dict]:
        """Extract account details from a single account block"""
        
        # Creditor name cleanup
        name = creditor_name.strip().title()
        
        # Extract balance
        balance = 0.0
        balance_match = re.search(r'balance\s*[:\-]?\s*\$?([\d,]+(?:\.\d{2})?)', block_text, re.IGNORECASE)
        if balance_match:
            try:
                balance = float(balance_match.group(1).replace(',', ''))
                print(f"[EquifaxExtractor] Found balance: ${balance}")
            except ValueError:
                balance = 0.0
        
        # Extract account number
        account_number = None
        acct_match = re.search(r'account\s+number\s*[:\-]?\s*\*?([A-Z0-9]+)', block_text, re.IGNORECASE)
        if acct_match:
            account_number = acct_match.group(1).strip()
            print(f"[EquifaxExtractor] Found account number: {account_number}")
        
        # Extract account type
        account_type = 'other'
        type_match = re.search(r'(?:loan|account)\s*/?[/]?type\s*[:\-]?\s*(.+?)(?:\n|$)', block_text, re.IGNORECASE)
        if type_match:
            type_str = type_match.group(1).strip()
            account_type = self.normalize_account_type(type_str)
            print(f"[EquifaxExtractor] Found account type: {type_str} → {account_type}")
        
        # Extract credit limit (for revolving accounts)
        limit = None
        limit_match = re.search(r'(?:credit\s+limit|limit|credit line)\s*[:\-]?\s*\$?([\d,]+(?:\.\d{2})?)', block_text, re.IGNORECASE)
        if limit_match:
            try:
                limit_val = float(limit_match.group(1).replace(',', ''))
                if limit_val > 0:
                    limit = limit_val
                    print(f"[EquifaxExtractor] Found credit limit: ${limit}")
            except ValueError:
                pass
        
        # Extract high credit (also used for limit)
        if not limit:
            high_credit_match = re.search(r'high\s+credit\s*[:\-]?\s*\$?([\d,]+(?:\.\d{2})?)', block_text, re.IGNORECASE)
            if high_credit_match:
                try:
                    limit = float(high_credit_match.group(1).replace(',', ''))
                    print(f"[EquifaxExtractor] Found high credit: ${limit}")
                except ValueError:
                    pass
        
        # Extract date opened
        open_date = date.today().isoformat()
        date_match = re.search(r'date\s+(?:opened|open)\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})', block_text, re.IGNORECASE)
        if date_match:
            parsed = self.parse_date(date_match.group(1))
            if parsed:
                open_date = parsed
                print(f"[EquifaxExtractor] Found date opened: {open_date}")
        
        # Normalize status
        normalized_status = self.normalize_status(status_str)
        print(f"[EquifaxExtractor] Normalized status: {status_str} → {normalized_status}")
        
        return {
            'name': name,
            'type': account_type,
            'balance': balance,
            'limit': limit,
            'open_date': open_date,
            'status': normalized_status,
        }
    
    def _fallback_extraction(self) -> List[Dict]:
        """Fallback: use line-by-line extraction if block segmentation fails"""
        accounts = []
        lines = self.lines
        current_account = {}
        
        for line in lines:
            line_stripped = line.strip()
            
            # Look for standalone creditor names (all caps, no labels)
            if re.match(r'^[A-Z][A-Z0-9\s/,&.\-]*$', line_stripped) and len(line_stripped) > 5 and len(line_stripped) < 80:
                # This might be an account name header
                if current_account and 'name' in current_account:
                    accounts.append(current_account)
                current_account = {'name': line_stripped.title()}
                continue
            
            # Extract balance from labeled lines
            balance_match = re.search(r'balance\s*[:\-]?\s*\$?([\d,]+(?:\.\d{2})?)', line_stripped, re.IGNORECASE)
            if balance_match:
                try:
                    current_account['balance'] = float(balance_match.group(1).replace(',', ''))
                except ValueError:
                    pass
            
            # Extract status
            status_match = re.search(r'status\s*[:\-]?\s*(.+)$', line_stripped, re.IGNORECASE)
            if status_match and 'status' not in current_account:
                current_account['status'] = self.normalize_status(status_match.group(1))
        
        if current_account and 'name' in current_account:
            accounts.append(current_account)
        
        # Validate and set defaults
        validated = []
        for account in accounts:
            if 'name' in account and len(account['name'].strip()) > 3:
                account.setdefault('type', 'other')
                account.setdefault('balance', 0.0)
                account.setdefault('limit', None)
                account.setdefault('open_date', date.today().isoformat())
                account.setdefault('status', 'active')
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


class CreditKarmaExtractor(AccountExtractor):
    """Extract accounts from Credit Karma credit reports (universal format that works with any bureau)"""
    
    def extract_accounts(self) -> List[Dict]:
        """
        Extract accounts using heuristics that work with Credit Karma formatting.
        Credit Karma shows accounts in a table-like format with consistent patterns.
        """
        accounts = []
        lines = self.lines
        
        # Look for account name patterns
        # Credit Karma typically has patterns like:
        # - Bold/highlighted account names
        # - Followed by account type (Card, Loan, etc)
        # - Balance information  
        # - Status information
        
        current_account = {}
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Skip empty lines and common headers
            if not line_stripped or any(x in line_stripped.lower() for x in ['account', 'accounts', 'credit karma', 'report', '---', '===', 'page']):
                continue
            
            # Look for account names (common patterns from credit reports)
            # These usually don't have field labels
            if self._looks_like_account_name(line_stripped):
                if current_account and 'name' in current_account:
                    accounts.append(current_account)
                current_account = {'name': line_stripped}
            
            # Extract account type
            elif 'type' in line_stripped.lower() or any(atype in line_stripped.lower() for atype in ['credit card', 'auto loan', 'mortgage', 'student loan', 'personal', 'installment', 'revolving', 'fixed']):
                if current_account:
                    match = re.search(r'(credit\s+card|auto\s+loan|mortgage|student\s+loan|personal|charge\s+card|home\s+equity|installment|revolving|fixed)', line_stripped, re.IGNORECASE)
                    if match:
                        current_account['type'] = self.normalize_account_type(match.group(1))
            
            # Extract balance/current balance
            elif re.search(r'(balance|owed|current balance|amount due)\s*[:\-]?\s*[\$]?[\d,\.]+', line_stripped, re.IGNORECASE):
                if current_account:
                    match = re.search(r'(balance|owed|amount due|current balance)\s*[:\-]?\s*[\$]?([\d,\.]+)', line_stripped, re.IGNORECASE)
                    if match:
                        try:
                            balance_str = match.group(2).replace(',', '')
                            current_account['balance'] = float(balance_str)
                        except:
                            pass
            
            # Extract credit limit
            elif re.search(r'(limit|credit limit|high credit|max)\s*[:\-]?\s*[\$]?[\d,\.]+', line_stripped, re.IGNORECASE):
                if current_account:
                    match = re.search(r'(limit|credit limit|high credit|max)\s*[:\-]?\s*[\$]?([\d,\.]+)', line_stripped, re.IGNORECASE)
                    if match:
                        try:
                            limit_str = match.group(2).replace(',', '')
                            current_account['limit'] = float(limit_str)
                        except:
                            pass
            
            # Extract status
            elif re.search(r'(status|account status|condition)\s*[:\-]?\s*', line_stripped, re.IGNORECASE):
                if current_account:
                    match = re.search(r'(status|condition)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE)
                    if match:
                        current_account['status'] = self.normalize_status(match.group(2))
            
            # Extract date opened
            elif re.search(r'(opened|date opened|opened date|since)\s*[:\-]?\s*', line_stripped, re.IGNORECASE):
                if current_account:
                    match = re.search(r'(opened|opened date|since)\s*[:\-]?\s*(.+)', line_stripped, re.IGNORECASE)
                    if match:
                        parsed_date = self.parse_date(match.group(2))
                        if parsed_date:
                            current_account['open_date'] = parsed_date
        
        if current_account and 'name' in current_account:
            accounts.append(current_account)
        
        # Validate and set defaults
        return self._validate_accounts(accounts)
    
    def _looks_like_account_name(self, text: str) -> bool:
        """Heuristic to identify if text is likely an account name"""
        if len(text) < 3 or len(text) > 100:
            return False
        
        # EXCLUDE: These are definitely not account names
        exclude_keywords = [
            'balance', 'status', 'opened', 'limit', 'type:', 'page', 'credit karma',
            'report', 'accounts', 'total', 'summary', 'score', 'rating',  'inquiry',
            'derogatory', 'payment', 'history', 'utilization', 'percentage', 'annual', 'monthly',
            'your', 'the', 'and', 'or', 'account number', 'inquiries', 'accounts'
        ]
        
        text_lower = text.lower()
        for keyword in exclude_keywords:
            if keyword in text_lower:
                return False
        
        # EXCLUDE: Line with currency amounts
        if '$' in text and re.search(r'\$\s*[\d,]+', text):
            return False
        
        # EXCLUDE: Date format lines
        if re.search(r'^\d{1,2}/\d{1,2}/\d{2,4}$', text):
            return False
        
        # EXCLUDE: Just numbers
        if re.search(r'^\d+$', text):
            return False
        
        # INCLUDE: Known financial institutions (strong match)
        strong_indicators = [
            'chase', 'bank of america', 'Wells Fargo', 'wells', 'citibank', 'amex', 
            'american express', 'discover', 'capital one', 'barclays', 'synchrony', 
            'us bank', 'navy federal'
        ]
        
        for indicator in strong_indicators:
            if indicator.lower() in text_lower:
                return True
        
        # INCLUDE: Contains specific account type keywords
        if any(x.lower() in text_lower for x in ['credit card', 'checking', 'savings', 'auto loan', 'mortgage']):
            return True
        
        # Only accept capitalized phrases that are truly account-like
        # Single word: max 20 chars (like "Chase" or "Discover")
        if len(text.split()) == 1:
            if text[0].isupper() and 3 <= len(text) <= 20:
                # But exclude common generic words
                if text.lower() not in ['account', 'total', 'payment', 'balance']:
                    return True
        
        # Two-three words: like "Chase Sapphire" or "Bank of America"
        elif 2 <= len(text.split()) <= 3:
            # All words must be capitalized
            words = text.split()
            if all(word and word[0].isupper() for word in words):
                # Must not be a sentence (no verbs)
                if not any(word.lower() in ['is', 'was', 'are', 'been', 'have', 'has', 'does'] for word in words):
                    # Additional check: not too short per word (avoids "A B C" etc)
                    if all(len(word) >= 2 for word in words):
                        return True
        
        return False
    
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
            print(f"PDF text extraction successful. Extracted {len(text)} characters")
            print(f"First 500 chars: {text[:500]}")
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            print(f"TXT file read. Extracted {len(text)} characters")

        # If no usable text, try OCR fallback
        if not text or len(text.strip()) < 120:
            print(f"Text too short ({len(text)} chars), attempting OCR...")
            try:
                ocr_text = extract_text_with_ocr(file_path)
                if ocr_text and len(ocr_text.strip()) > 50:
                    print(f"OCR successful, extracted {len(ocr_text)} characters")
                    text = ocr_text
            except Exception as e:
                print(f"OCR failed: {str(e)}")
                pass

        if not text or len(text.strip()) < 100:
            return [], "Could not extract sufficient text from file"
        
        print(f"\n=== PARSING WITH BUREAU: {bureau.value.upper()} ===")
        
        # Try Credit Karma extractor first (works universally for Credit Karma format)
        if 'credit karma' in text.lower():
            print(f"Detected 'Credit Karma' in text, using CreditKarmaExtractor...")
            ck_extractor = CreditKarmaExtractor(text)
            accounts = ck_extractor.extract_accounts()
            print(f"CreditKarmaExtractor returned {len(accounts)} accounts")
            if accounts:
                status = f"Successfully extracted {len(accounts)} account(s) from Credit Karma report"
                return accounts, status
        
        # Select appropriate extractor based on bureau
        print(f"Using bureau-specific extractor: {bureau.value}")
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
        print(f"Bureau extractor returned {len(accounts)} accounts")

        # Additional heuristic pass: use extractor's fallback heuristics to find creditor blocks
        if not accounts:
            print(f"No accounts found, trying additional heuristics...")
            accounts = extractor.run_additional_heuristics()
            print(f"Additional heuristics returned {len(accounts)} accounts")
        
        # If still no accounts, try Credit Karma extractor as last resort
        if not accounts:
            print(f"Still no accounts, trying CreditKarmaExtractor as fallback...")
            ck_extractor = CreditKarmaExtractor(text)
            accounts = ck_extractor.extract_accounts()
            print(f"CreditKarmaExtractor fallback returned {len(accounts)} accounts")
        
        status = f"Successfully extracted {len(accounts)} account(s) from {bureau.value} report"
        print(f"Final result: {status}")
        print(f"=== PARSING COMPLETE ===\n")
        return accounts, status
    
    except Exception as e:
        import traceback
        print(f"ERROR during parsing: {str(e)}")
        traceback.print_exc()
        return [], f"Error parsing report: {str(e)}"
