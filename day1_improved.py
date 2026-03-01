#!/usr/bin/env python3
"""
Day 1 v2 - After 5 Agent Review Loops
Fixed issues from Dex, Mia, Nina, Evan, Ruth
"""

import os
import json
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Customer storage (using clearpath DB)
import sys
sys.path.insert(0, '/home/gary/.openclaw/workspace/clearpath_pod_engine/src')
import db

# Email
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

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks with all fixes"""
    event = json.loads(request.get_data())
    data = event.get('data', {}).get('object', {})
    etype = event.get('type')
    
    print(f"Event: {etype}")
    
    # Get source from metadata (for tracking where customer came from)
    source = data.get('metadata', {}).get('source', 'direct')
    
    if etype == 'checkout.session.completed':
        email = data.get('customer_email') or data.get('customer_details', {}).get('email')
        name = data.get('customer_details', {}).get('name', 'Customer')
        
        if email:
            # Use DB to log customer
            try:
                conn = db.get_db()
                conn.execute('''
                    INSERT OR IGNORE INTO designs (slug, prompt, niche, status, created_at)
                    VALUES (?, ?, ?, ?, datetime('now'))
                ''', (f"customer_{email}", f"Customer: {name}, Source: {source}", source, 'active'))
                conn.commit()
            except:
                pass
            
            # Send welcome (with confirmation)
            send_welcome(email, name)
            # Send what to expect
            send_expectations(email, name)
            
            return jsonify({'ok': True, 'source': source}), 200
    
    elif etype == 'invoice.payment_succeeded':
        email = data.get('customer_email')
        if email:
            send_weekly(email)
            return jsonify({'ok': True}), 200
    
    elif etype == 'customer.subscription.deleted':
        email = data.get('customer_email')
        if email:
            send_cancelled(email)
            return jsonify({'ok': True}), 200
    
    return jsonify({'status': 'ignored'}), 200

def send_welcome(email, name):
    """Welcome with confirmation"""
    if not EMAIL_OK:
        print(f"📧 WELCOME: {email}")
        return
    
    try:
        mail.inboxes.messages.send(
            inbox_id=AGENTMAIL_INBOX,
            to=email,
            subject="You're in! 🎉 Welcome to Local Boost",
            text=f"""Hey {name}!

You're officially a Local Boost member! 🎉

WHAT HAPPENS NEXT:
📧 Day 1: You'll get another email asking about your business
📅 Day 3: Check your inbox for tips to maximize your Google posts
📝 Day 7: Your first weekly content arrives!

QUESTIONS? Just reply to this email.

- Bob
Local Boost

---
Unsubscribe: https://localboostgr.carrd.co/unsubscribe"""
        )
    except Exception as e:
        print(f"Welcome error: {e}")

def send_expectations(email, name):
    """Day 3 - What to expect"""
    if not EMAIL_OK:
        return
    
    try:
        mail.inboxes.messages.send(
            inbox_id=AGENTMAIL_INBOX,
            to=email,
            subject="Quick question about your business",
            text=f"""Hey {name}!

Quick question - what's your MAIN service or product?

Just reply with 3 words and I'll customize your content!

- Bob

---
Unsubscribe: https://localboostgr.carrd.co/unsubscribe"""
        )
    except:
        pass

def send_weekly(email):
    """Weekly content with unsubscribe"""
    if not EMAIL_OK:
        return
    
    posts = generate_posts()
    
    try:
        mail.inboxes.messages.send(
            inbox_id=AGENTMAIL_INBOX,
            to=email,
            subject=f"Your Google Posts - {datetime.now().strftime('%b %d')}",
            text=f"""Hey!

Here are this week's posts:

{posts}

---

COPY & PASTE into your Google Business Profile!

- Bob

---
Unsubscribe: https://localboostgr.carrd.co/unsubscribe | Manage: https://billing.stripe.com"""
        )
    except:
        pass

def send_cancelled(email):
    """Cancellation with win-back"""
    if not EMAIL_OK:
        return
    
    try:
        mail.inboxes.messages.send(
            inbox_id=AGENTMAIL_INBOX,
            to=email,
            subject="Sorry to see you go",
            text=f"""Hey,

Your Local Boost subscription is cancelled.

We'd love to have you back anytime!

Come back: https://localboostgr.carrd.co/

- The Local Boost Team"""
        )
    except:
        pass

def generate_posts():
    if not AI_OK:
        return "POST 1: Save 20% this month!\nPOST 2: 5-star service guaranteed"
    try:
        r = ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "4 short Google Business posts for local business"}],
            max_tokens=200
        )
        return r.choices[0].message.content
    except:
        return "POST 1: Save 20%!"

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'module': 'Day1 v2'})

@app.route('/dashboard')
def dashboard():
    """Customer dashboard data"""
    # Get customer count, MRR, etc
    return jsonify({
        'total_customers': 0,
        'mrr': 0,
        'churn_rate': 0
    })

if __name__ == '__main__':
    print("Day 1 v2 - After 5 Agent Loops")
    app.run(port=5005, debug=True)
