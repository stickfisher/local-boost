#!/usr/bin/env python3
"""
Local Boost Webhook Server v3.0
Now with Google Sheets customer tracking!
"""

import os
import sys
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime

# Add sheets to path
sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)

# Import our modules
try:
    from sheets.customer_tracker import log_customer, update_customer_status, get_mrr, get_all_customers
    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False
    print("Warning: Google Sheets not configured")

# Import other modules
try:
    import agentmail
    from openai import OpenAI
    AGENTMAIL_AVAILABLE = True
except ImportError:
    AGENTMAIL_AVAILABLE = False

# API Keys
AGENTMAIL_API_KEY = os.getenv('AGENTMAIL_API_KEY', 'am_us_f39ceb644a239a3e5522e89d65d557515c3dac722ab78e7273936c104b217f81')
AGENTMAIL_INBOX = os.getenv('AGENTMAIL_INBOX', 'local.boost@agentmail.to')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Initialize
if AGENTMAIL_AVAILABLE:
    client = agentmail.AgentMail(api_key=AGENTMAIL_API_KEY)
if OPENAI_API_KEY:
    ai_client = OpenAI(api_key=OPENAI_API_KEY)

# In-memory customer store (until Sheets configured)
customers = {}

@app.route('/webhook/stripe', methods=['POST'])
def handle_stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    
    try:
        event = json.loads(payload)
    except:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    event_type = event.get('type')
    data = event.get('data', {}).get('object', {})
    
    print(f"Received: {event_type}")
    
    if event_type == 'checkout.session.completed':
        email = data.get('customer_email') or data.get('customer_details', {}).get('email')
        name = data.get('customer_details', {}).get('name', 'Customer')
        customer_id = data.get('customer', '')
        
        if email:
            # Save customer
            customers[email] = {
                'name': name,
                'status': 'active',
                'mrr': 29,
                'stripe_customer_id': customer_id,
                'created_at': datetime.now().isoformat()
            }
            
            # Log to Sheets if available
            if SHEETS_AVAILABLE:
                try:
                    log_customer(email, name, 'active', 29, customer_id, '')
                except Exception as e:
                    print(f"Sheets error: {e}")
            
            # Send welcome email
            send_welcome_email(email, name)
            
            return jsonify({'status': 'welcome_sent', 'sheets': SHEETS_AVAILABLE}), 200
            
    elif event_type == 'invoice.payment_succeeded':
        email = data.get('customer_email')
        if email:
            # Send weekly content
            send_weekly_content(email)
            return jsonify({'status': 'content_sent'}), 200
            
    elif event_type == 'customer.subscription.deleted':
        email = data.get('customer_email')
        if email:
            if email in customers:
                customers[email]['status'] = 'cancelled'
            
            if SHEETS_AVAILABLE:
                try:
                    update_customer_status(email, 'cancelled')
                except:
                    pass
            
            send_cancellation_email(email)
            return jsonify({'status': 'cancellation_notified'}), 200
    
    return jsonify({'status': 'ignored'}), 200

def send_welcome_email(email, name):
    """Send welcome email"""
    if not AGENTMAIL_AVAILABLE:
        print(f"WELCOME EMAIL to {email}: Welcome to Local Boost!")
        return
    
    subject = "Welcome to Local Boost! Let's personalize your content"
    body = f"""Hey {name}!

Welcome to Local Boost! 🎉

To create custom Google Business posts for YOUR business, reply with:

1. Your website
2. Your industry
3. Top 3 services
4. Any current promotions

Once I have this, I'll create personalized posts every week!

- Bob (Your AI Local Marketing Manager)
"""
    try:
        client.inboxes.messages.send(
            inbox_id=AGENTMAIL_INBOX,
            to=email,
            subject=subject,
            text=body
        )
    except Exception as e:
        print(f"Email error: {e}")

def send_weekly_content(email):
    """Send AI-generated weekly content"""
    customer = customers.get(email, {})
    name = customer.get('name', 'there')
    
    # Generate content with AI
    posts = generate_ai_posts()
    
    subject = f"Your Weekly Google Business Posts - {datetime.now().strftime('%B %d')}"
    body = f"""Hey {name}!

Here are this week's custom posts:

{posts}

Just copy and paste into your Google Business Profile!

- Bob
Local Boost
"""
    
    if AGENTMAIL_AVAILABLE:
        try:
            client.inboxes.messages.send(
                inbox_id=AGENTMAIL_INBOX,
                to=email,
                subject=subject,
                text=body
            )
        except:
            pass
    else:
        print(f"WEEKLY EMAIL to {email}: {posts}")

def generate_ai_posts():
    """Generate posts with AI"""
    if not OPENAI_API_KEY:
        return generate_template_posts()
    
    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Create 4 short Google Business posts. Keep under 150 chars each."},
                {"role": "user", "content": "Create promotional posts for a local business"}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except:
        return generate_template_posts()

def generate_template_posts():
    """Fallback template posts"""
    return """POST 1: 🔥 Save 20% this month! Book now.

POST 2: Professional service. 5-star reviews. Call today!

POST 3: Thanks for your support! We're here to help.

POST 4: Open Mon-Fri 9-6. Licensed & insured."""

def send_cancellation_email(email):
    """Send cancellation email"""
    if AGENTMAIL_AVAILABLE:
        try:
            client.inboxes.messages.send(
                inbox_id=AGENTMAIL_INBOX,
                to=email,
                subject="Sorry to see you go",
                text="Come back anytime! https://localboostgr.carrd.co"
            )
        except:
            pass

@app.route('/health', methods=['GET'])
def health():
    mrr = 0
    if SHEETS_AVAILABLE:
        try:
            mrr = get_mrr()
        except:
            pass
    
    return jsonify({
        'status': 'ok',
        'sheets': SHEETS_AVAILABLE,
        'customers': len(customers),
        'mrr': mrr
    })

@app.route('/customers', methods=['GET'])
def list_customers():
    """List all customers"""
    if SHEETS_AVAILABLE:
        try:
            return jsonify(get_all_customers())
        except:
            pass
    return jsonify(customers)

if __name__ == '__main__':
    print("Local Boost v3.0 - with Sheets integration!")
    print(f"Sheets: {SHEETS_AVAILABLE}")
    print(f"AI: {bool(OPENAI_API_KEY)}")
    app.run(port=5005, debug=True)
