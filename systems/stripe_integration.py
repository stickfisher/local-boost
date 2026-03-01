"""
Local Boost - Stripe Integration v1.0
Payment processing and webhook handling
"""

import os
import json
import hmac
import hashlib
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from customer_db import add_customer, update_status, log_payment

STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')

def verify_signature(payload, signature):
    """Verify Stripe webhook signature"""
    if not STRIPE_WEBHOOK_SECRET:
        return True  # Skip in dev
    
    expected = hmac.new(
        STRIPE_WEBHOOK_SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)

def handle_webhook(event):
    """Process Stripe webhook event"""
    etype = event.get('type')
    data = event.get('data', {}).get('object', {})
    
    print(f"Stripe event: {etype}")
    
    if etype == 'checkout.session.completed':
        return handle_checkout(data)
    
    elif etype == 'invoice.payment_succeeded':
        return handle_payment(data)
    
    elif etype == 'customer.subscription.deleted':
        return handle_cancellation(data)
    
    elif etype == 'customer.subscription.updated':
        return handle_subscription_update(data)
    
    return {'status': 'ignored'}

def handle_checkout(data):
    """Handle new subscription"""
    email = data.get('customer_email') or data.get('customer_details', {}).get('email')
    name = data.get('customer_details', {}).get('name', 'Customer')
    customer_id = data.get('customer', '')
    subscription_id = data.get('subscription', '')
    
    if email:
        add_customer(
            email=email,
            name=name,
            status='active',
            source=data.get('metadata', {}).get('source', 'direct'),
            stripe_cust_id=customer_id,
            stripe_sub_id=subscription_id
        )
        
        return {'status': 'customer_created', 'email': email}
    
    return {'status': 'no_email'}

def handle_payment(data):
    """Handle successful payment"""
    email = data.get('customer_email')
    amount = data.get('amount_paid', 0) // 100  # Convert cents
    payment_id = data.get('id', '')
    
    if email:
        log_payment(email, amount, payment_id)
        return {'status': 'payment_logged', 'email': email, 'amount': amount}
    
    return {'status': 'no_email'}

def handle_cancellation(data):
    """Handle subscription cancellation"""
    email = data.get('customer_email')
    
    if email:
        update_status(email, 'cancelled')
        return {'status': 'cancelled', 'email': email}
    
    return {'status': 'no_email'}

def handle_subscription_update(data):
    """Handle subscription changes"""
    email = data.get('customer_email')
    status = data.get('status')
    
    if email and status:
        if status == 'active':
            update_status(email, 'active')
        elif status == 'canceled':
            update_status(email, 'cancelled')
    
    return {'status': 'updated'}

def create_checkout_session(email, price_id='price_xxx'):
    """Create Stripe checkout session (would call Stripe API)"""
    # In production, use stripe library
    return {
        'url': f'https://checkout.stripe.com/c/pay/{price_id}',
        'session_id': 'cs_xxx'
    }

def create_customer(email, name=''):
    """Create Stripe customer"""
    return {'id': 'cus_xxx', 'email': email}

if __name__ == '__main__':
    # Test webhook handling
    test_event = {
        'type': 'checkout.session.completed',
        'data': {
            'object': {
                'customer_email': 'test@example.com',
                'customer_details': {'name': 'Test User'},
                'customer': 'cus_123',
                'subscription': 'sub_456'
            }
        }
    }
    
    result = handle_webhook(test_event)
    print(f"Test result: {result}")
