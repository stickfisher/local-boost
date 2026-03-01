"""
Simple Customer Tracker - Works without Google credentials
Uses CSV file for tracking
"""

import csv
import os
from datetime import datetime
from pathlib import Path

TRACKER_FILE = Path(__file__).parent / 'customers.csv'

def init_tracker():
    """Initialize CSV file if not exists"""
    if not TRACKER_FILE.exists():
        with open(TRACKER_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Email', 'Name', 'Status', 'MRR', 'Source'])

def log_customer(email, name, status='active', mrr=29, source='stripe'):
    """Log a new customer"""
    init_tracker()
    
    # Check if email already exists
    existing = []
    with open(TRACKER_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Email'] == email:
                existing.append(row)
    
    if len(existing) > 0:
        # Update existing
        update_customer_status(email, status)
        return False
    
    # Add new
    with open(TRACKER_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M'),
            email,
            name,
            status,
            mrr,
            source
        ])
    
    print(f"✓ Logged: {email} ({status})")
    return True

def update_customer_status(email, new_status):
    """Update customer status"""
    init_tracker()
    
    rows = []
    updated = False
    
    with open(TRACKER_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Email'] == email:
                row['Status'] = new_status
                updated = True
            rows.append(row)
    
    if updated:
        with open(TRACKER_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['Date', 'Email', 'Name', 'Status', 'MRR', 'Source'])
            writer.writeheader()
            writer.writerows(rows)
        print(f"✓ Updated: {email} → {new_status}")
    
    return updated

def get_all_customers():
    """Get all customers"""
    init_tracker()
    
    customers = []
    with open(TRACKER_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            customers.append(row)
    return customers

def get_mrr():
    """Calculate MRR"""
    customers = get_all_customers()
    return sum(int(c.get('MRR', 0)) for c in customers if c.get('Status') == 'active')

def get_customer_count():
    """Get total customer count"""
    return len(get_all_customers())

if __name__ == '__main__':
    # Test
    print("=== Customer Tracker Test ===")
    
    # Add test customer
    log_customer('test@example.com', 'Test User', 'active', 29, 'test')
    
    # Get stats
    print(f"\nCustomers: {get_customer_count()}")
    print(f"MRR: ${get_mrr()}")
    
    # List all
    print("\nAll customers:")
    for c in get_all_customers():
        print(f"  {c['Email']}: {c['Status']} - ${c['MRR']}")
