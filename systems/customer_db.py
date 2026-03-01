"""
Local Boost - Customer Management System v1.0
Complete customer lifecycle management
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'data' / 'customers.db'

def get_db():
    """Get database connection"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize customer table"""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            status TEXT DEFAULT 'lead',
            source TEXT DEFAULT 'direct',
            mrr INTEGER DEFAULT 29,
            stripe_customer_id TEXT,
            stripe_subscription_id TEXT,
            subscribed_at TEXT,
            cancelled_at TEXT,
            lifetime_value INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS email_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_email TEXT,
            event_type TEXT,
            sent_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_email TEXT,
            amount INTEGER,
            currency TEXT DEFAULT 'usd',
            stripe_payment_id TEXT,
            paid_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    return DB_PATH

def add_customer(email, name='', status='lead', source='direct', stripe_cust_id='', stripe_sub_id=''):
    """Add or update customer"""
    conn = get_db()
    now = datetime.now().isoformat()
    
    conn.execute('''
        INSERT OR REPLACE INTO customers 
        (email, name, status, source, stripe_customer_id, stripe_subscription_id, subscribed_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (email, name, status, source, stripe_cust_id, stripe_sub_id, now, now))
    conn.commit()
    return get_customer(email)

def get_customer(email):
    """Get customer by email"""
    conn = get_db()
    row = conn.execute('SELECT * FROM customers WHERE email = ?', (email,)).fetchone()
    return dict(row) if row else None

def get_all_customers(status=None):
    conn = get_db()
    if status:
        rows = conn.execute('SELECT * FROM customers WHERE status = ?', (status,)).fetchall()
    else:
        rows = conn.execute('SELECT * FROM customers').fetchall()
    return [dict(r) for r in rows]

def update_status(email, new_status):
    conn = get_db()
    now = datetime.now().isoformat()
    conn.execute('UPDATE customers SET status = ?, updated_at = ? WHERE email = ?',
                 (new_status, now, email))
    conn.commit()

def log_payment(email, amount, stripe_payment_id):
    conn = get_db()
    conn.execute('INSERT INTO payments (customer_email, amount, stripe_payment_id) VALUES (?, ?, ?)',
                 (email, amount, stripe_payment_id))
    conn.execute('UPDATE customers SET lifetime_value = lifetime_value + ? WHERE email = ?',
                 (amount, email))
    conn.commit()

def get_mrr():
    conn = get_db()
    result = conn.execute("SELECT SUM(mrr) as total FROM customers WHERE status = 'active'").fetchone()
    return result['total'] or 0

def get_stats():
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) as c FROM customers').fetchone()['c']
    active = conn.execute("SELECT COUNT(*) as c FROM customers WHERE status = 'active'").fetchone()['c']
    mrr = active * 29
    ltv = conn.execute('SELECT SUM(lifetime_value) as t FROM customers').fetchone()['t'] or 0
    return {'total': total, 'active': active, 'mrr': mrr, 'ltv': ltv}

if __name__ == '__main__':
    path = init_db()
    print(f"DB: {path}")
    print(get_stats())

def log_email_event(email, event_type):
    conn = get_db()
    conn.execute('INSERT INTO email_events (customer_email, event_type) VALUES (?, ?)', 
                 (email, event_type))
    conn.commit()
