#!/usr/bin/env python3
"""
Day 1 Complete: Customer Tracker + Email Automation
"""

import os
import json
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Import trackers
from sheets.simple_tracker import log_customer, update_customer_status, get_mrr, get_all_customers

# Email automation
AGENTMAIL_KEY = os.getenv('AGENTMAIL_API_KEY', 'am_us_f39ceb644a239a3e5522e89d65d557515c3dac722ab78e7273936c104b217f81')
AGENTMAIL_INBOX = 'local.boost@agentmail.to'
OPENAI_KEY = os.getenv('OPENAI_API_KEY', '')

try:
    import agentmail
    from openai import OpenAI
    EMAIL_OK = True
    AI_OK = bool(OPENAI_KEY)
except:
    EMAIL_OK = False
    AI_OK = False

if EMAIL_OK:
    mail = agentmail.AgentMail(api_key=AGENTMAIL_KEY)
if AI_OK:
    ai = OpenAI(api_key=OPENAI_KEY)

# Track customers in memory too
customers = {}

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    event = json.loads(request.get_data())
    data = event.get('data', {}).get('object', {})
    etype = event.get('type')
    
    print(f"Event: {etype}")
    
    if etype == 'checkout.session.completed':
        email = data.get('customer_email') or data.get('customer_details', {}).get('email')
        name = data.get('customer_details', {}).get('name', 'Customer')
        
        if email:
            customers[email] = {'name': name, 'status': 'active', 'mrr': 29}
            log_customer(email, name, 'active', 29, 'stripe')
            send_welcome(email, name)
            return jsonify({'ok': True}), 200
    
    elif etype == 'invoice.payment_succeeded':
        email = data.get('customer_email')
        if email:
            send_weekly(email)
            return jsonify({'ok': True}), 200
    
    elif etype == 'customer.subscription.deleted':
        email = data.get('customer_email')
        if email:
            customers[email]['status'] = 'cancelled'
            update_customer_status(email, 'cancelled')
            send_cancelled(email)
            return jsonify({'ok': True}), 200
    
    return jsonify({'status': 'ignored'}), 200

def send_welcome(email, name):
    if not EMAIL_OK:
        print(f"📧 WELCOME to {email}")
        return
    
    try:
        mail.inboxes.messages.send(
            inbox_id=AGENTMAIL_INBOX,
            to=email,
            subject="Welcome to Local Boost!",
            text=f"""Hey {name}!

Welcome! 🎉

Reply with:
1. Your website
2. Industry  
3. Top services
4. Current promotions

I'll create custom posts every week!

- Bob"""
        )
    except Exception as e:
        print(f"Email error: {e}")

def send_weekly(email):
    customer = customers.get(email, {})
    name = customer.get('name', 'there')
    posts = generate_posts()
    
    if not EMAIL_OK:
        print(f"📧 WEEKLY to {email}: {posts[:50]}...")
        return
    
    try:
        mail.inboxes.messages.send(
            inbox_id=AGENTMAIL_INBOX,
            to=email,
            subject=f"Your Weekly Posts - {datetime.now().strftime('%b %d')}",
            text=f"Hey {name}!\n\n{posts}\n\n- Bob"
        )
    except:
        pass

def send_cancelled(email):
    if EMAIL_OK:
        try:
            mail.inboxes.messages.send(
                inbox_id=AGENTMAIL_INBOX,
                to=email,
                subject="Sorry to see you go",
                text="Come back anytime! https://localboostgr.carrd.co"
            )
        except:
            pass

def generate_posts():
    if not AI_OK:
        return "POST 1: Save 20%! POST 2: 5-star service. POST 3: Thanks! POST 4: Open Mon-Fri"
    
    try:
        r = ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "4 short business posts"}],
            max_tokens=200
        )
        return r.choices[0].message.content
    except:
        return "POST 1: Save 20%! POST 2: 5-star service"

@app.route('/health')
def health():
    return jsonify({
        'customers': get_customer_count(),
        'mrr': get_mrr(),
        'email_ok': EMAIL_OK,
        'ai_ok': AI_OK
    })

@app.route('/customers')
def list_customers():
    return jsonify(get_all_customers())

if __name__ == '__main__':
    print("=" * 40)
    print("Day 1 Complete: Customer Tracker")
    print(f"Customers: {get_customer_count()}")
    print(f"MRR: ${get_mrr()}")
    print("=" * 40)
    app.run(port=5005, debug=True)
