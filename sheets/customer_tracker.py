"""
Local Boost - Google Sheets Customer Tracker
Auto-logs new customers from Stripe to Google Sheets
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Google Sheets config
SHEET_NAME = "Local Boost Customers"
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_google_credentials():
    """Get Google credentials from env or service account file"""
    # Check for credentials in environment
    creds_json = os.getenv('GOOGLE_CREDS_JSON')
    
    if creds_json:
        import json
        from io import StringIO
        creds_dict = json.loads(creds_json)
        return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    
    # Check for file
    creds_file = os.path.expanduser('~/.google/credentials.json')
    if os.path.exists(creds_file):
        return Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    
    return None

def get_or_create_sheet():
    """Get or create the customer tracking sheet"""
    creds = get_google_credentials()
    if not creds:
        print("No Google credentials found. Set GOOGLE_CREDS_JSON or create ~/.google/credentials.json")
        return None, None
    
    gc = gspread.authorize(creds)
    
    try:
        sheet = gc.open(SHEET_NAME).sheet1
    except:
        # Create new spreadsheet
        gc.create(SHEET_NAME)
        sheet = gc.open(SHEET_NAME).sheet1
        # Add headers
        sheet.append_row([
            'Date', 'Email', 'Name', 'Status', 'MRR', 
            'Stripe Customer ID', 'Stripe Subscription ID', 'Source'
        ])
    
    return gc, sheet

def log_customer(email, name, status='active', mrr=29, stripe_customer_id='', stripe_sub_id='', source='stripe'):
    """Log a new customer to Google Sheets"""
    _, sheet = get_or_create_sheet()
    
    if sheet:
        row = [
            datetime.now().strftime('%Y-%m-%d %H:%M'),
            email,
            name,
            status,
            mrr,
            stripe_customer_id,
            stripe_sub_id,
            source
        ]
        sheet.append_row(row)
        print(f"Logged customer: {email}")
        return True
    
    return False

def update_customer_status(email, new_status):
    """Update a customer's status"""
    _, sheet = get_or_create_sheet()
    
    if sheet:
        # Find row with email
        all_rows = sheet.get_all_records()
        for i, row in enumerate(all_rows, start=2):
            if row.get('Email') == email:
                sheet.update_cell(i, 4, new_status)
                print(f"Updated {email} to {new_status}")
                return True
    
    return False

def get_all_customers():
    """Get all customers from sheet"""
    _, sheet = get_or_create_sheet()
    
    if sheet:
        return sheet.get_all_records()
    return []

def get_mrr():
    """Calculate Monthly Recurring Revenue"""
    customers = get_all_customers()
    active_mrr = sum(int(c.get('MRR', 0)) for c in customers if c.get('Status') == 'active')
    return active_mrr

if __name__ == '__main__':
    # Test
    print("Local Boost Customer Tracker")
    print(f"MRR: ${get_mrr()}")
