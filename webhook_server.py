#!/usr/bin/env python3
"""
Local Boost Webhook Server v2.1
Supports Minimax (primary) + OpenAI (fallback)
"""

import os
import json
import requests
from flask import Flask, request, jsonify
from agentmail import AgentMail
from datetime import datetime

app = Flask(__name__)

# API Keys
AGENTMAIL_API_KEY = os.getenv('AGENTMAIL_API_KEY', 'am_us_f39ceb644a239a3e5522e89d65d557515c3dac722ab78e7273936c104b217f81')
AGENTMAIL_INBOX = os.getenv('AGENTMAIL_INBOX', 'local.boost@agentmail.to')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_33s5TGZvgXxBXacFD5mUZwrM0VYRfewu')

# AI Providers
MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY', '')
MINIMAX_MODEL = os.getenv('MINIMAX_MODEL', 'MiniMax-Text-01')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

client = AgentMail(api_key=AGENTMAIL_API_KEY)

# Customer database
customers = {}

def generate_ai_posts(industry, services, website):
    """Generate posts using Minimax (primary) or OpenAI (fallback)"""
    
    # Try Minimax first
    if MINIMAX_API_KEY:
        try:
            posts = generate_minimax_posts(industry, services)
            print(f"Generated posts with Minimax")
            return posts
        except Exception as e:
            print(f"Minimax failed: {e}")
    
    # Fallback to OpenAI
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            ai_client = OpenAI(api_key=OPENAI_API_KEY)
            posts = generate_openai_posts(ai_client, industry, services)
            print(f"Generated posts with OpenAI")
            return posts
        except Exception as e:
            print(f"OpenAI failed: {e}")
    
    # Ultimate fallback: templates
    print("Using template fallback")
    return generate_template_posts(industry, services)

def generate_minimax_posts(industry, services):
    """Generate posts using Minimax API"""
    
    prompt = f"""Generate 4 creative Google Business posts for a {industry}.

Requirements:
- Post 1: Promotional/offer
- Post 2: Service highlight ({services[0] if services else 'main service'})
- Post 3: Community/engagement
- Post 4: Trust/quality

Rules:
- Keep each post under 150 characters
- Include relevant hashtags (1-2 max)
- Sound like a real local business
- Make it sound personal

Return ONLY the 4 posts, numbered 1-4."""
    
    url = "https://api.minimaxi.chat/v1/text/chatcompletion_pro"
    
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MINIMAX_MODEL,
        "messages": [
            {"role": "system", "content": "You are a local marketing expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 500
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    return result['choices'][0]['message']['content']

def generate_openai_posts(ai_client, industry, services):
    """Generate posts using OpenAI"""
    
    prompt = f"""Generate 4 creative Google Business posts for a {industry}.

Requirements:
- Post 1: Promotional/offer
- Post 2: Service highlight ({services[0] if services else 'main service'})
- Post 3: Community/engagement  
- Post 4: Trust/quality

Rules:
- Keep each post under 150 characters
- Include relevant hashtags (1-2 max)
- Sound like a real local business

Return ONLY the 4 posts, numbered 1-4."""
    
    response = ai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a local marketing expert."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.8
    )
    
    return response.choices[0].message.content

def generate_template_posts(industry, services):
    """Improved fallback templates"""
    service = services[0] if services else "our services"
    ind = industry.replace(" ", "").lower()
    
    return f"""POST 1 - Promotion:
🔥 Save 20% on {service} this month! Call now to book. Limited time! #{ind}

POST 2 - Service Highlight:
Professional {service} in town. 5-star service guaranteed. Learn more!

POST 3 - Community:
Thanks for supporting local business! Happy to serve our community! 🙏 #{ind}

POST 4 - Hours/Trust:
Open Mon-Fri 9am-6pm. Licensed & insured. Call today!"""

# ========== FLASK APP ==========

@app.route('/webhook/stripe', methods=['POST'])
def handle_stripe_webhook():
    payload = request.get_data()
    
    try:
        event = json.loads(payload)
    except:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    event_type = event.get('type')
    data = event.get('data', {}).get('object', {})
    
    print(f"Event: {event_type}")
    
    if event_type == 'checkout.session.completed':
        email = data.get('customer_email') or data.get('customer_details', {}).get('email')
        customer_name = data.get('customer_details', {}).get('name', 'Customer')
        
        if email:
            customers[email] = {
                'name': customer_name,
                'industry': None,
                'services': [],
                'website': None,
                'created_at': datetime.now().isoformat()
            }
            send_welcome_email(email, customer_name)
            return jsonify({'status': 'welcome_sent'}), 200
            
    elif event_type == 'invoice.payment_succeeded':
        email = data.get('customer_email')
        if email:
            send_weekly_ai_content(email)
            return jsonify({'status': 'content_sent'}), 200
            
    elif event_type == 'customer.subscription.deleted':
        email = data.get('customer_email')
        if email:
            send_cancellation_email(email)
    
    return jsonify({'status': 'ignored'}), 200

def send_welcome_email(email, name):
    subject = "Welcome to Local Boost! Let's personalize your content"
    body = f"""Hey {name}!

Welcome to Local Boost! 🎉

To create custom Google Business posts specifically for YOUR business, reply with:

1. Your website
2. Your industry  
3. Top 3 services
4. Any current promotions

Once I have this, I'll create personalized posts every week that sound like YOUR business!

- Bob (Your AI Local Marketing Manager)
"""
    client.inboxes.messages.send(
        inbox_id=AGENTMAIL_INBOX,
        to=email,
        subject=subject,
        text=body
    )

def send_weekly_ai_content(email):
    customer = customers.get(email, {})
    name = customer.get('name', 'there')
    industry = customer.get('industry') or 'local business'
    services = customer.get('services') or ['our services']
    
    posts = generate_ai_posts(industry, services, '')
    
    subject = f"Your Weekly Google Business Posts - {datetime.now().strftime('%B %d')}"
    body = f"""Hey {name}!

Here are this week's custom Google Business posts:

---

{posts}

---

Just copy and paste into your Google Business Profile!

Questions? Just reply!

- Bob
Local Boost
"""
    client.inboxes.messages.send(
        inbox_id=AGENTMAIL_INBOX,
        to=email,
        subject=subject,
        text=body
    )
    print(f"AI content sent to {email}")

def send_cancellation_email(email):
    subject = "Sorry to see you go - Local Boost"
    body = """Hey,

Sorry to see you go! Your Local Boost subscription has been cancelled.

Come back anytime: https://localboostgr.carrd.co/

- The Local Boost Team
"""
    client.inboxes.messages.send(
        inbox_id=AGENTMAIL_INBOX,
        to=email,
        subject=subject,
        text=body
    )

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'minimax': bool(MINIMAX_API_KEY),
        'openai': bool(OPENAI_API_KEY),
        'primary': 'minimax' if MINIMAX_API_KEY else ('openai' if OPENAI_API_KEY else 'templates')
    })

if __name__ == '__main__':
    print("Local Boost v2.1 - Minimax + OpenAI")
    print(f"Minimax: {'✓' if MINIMAX_API_KEY else '✗'}")
    print(f"OpenAI: {'✓' if OPENAI_API_KEY else '✗'}")
    app.run(port=5005, debug=True)
