#!/usr/bin/env python3
"""Local Boost"""

import os
import json
import requests
import hashlib
from flask import Flask, jsonify, request, redirect

app = Flask(__name__)

STRIPE_KEY = os.environ.get('STRIPE_KEY', 'sk_live_xxx')
PRICE = 'price_1T6GP2HZoCR3hYeR0HWrf084'
SB_URL = 'https://ohbxbyuwugulhhbwlubp.supabase.co'
SB_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9oYnhieXV3dWd1bGhoYndsdWJwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjM5ODM0OCwiZXhwIjoyMDg3OTc0MzQ4fQ.BtwwoiDAN4wMk14iAd3uQE6TLE1YVNPpbrsDRv4u4yA'
TOKEN_SECRET = 'local-boost-secret-2026'

def get_customer(email):
    r = requests.get(f"{SB_URL}/rest/v1/customers?email=eq.{email}", 
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"})
    if r.status_code == 200 and r.json():
        return r.json()[0]
    return None

def make_token(email):
    return hashlib.sha256(f"{email}{TOKEN_SECRET}".encode()).hexdigest()[:32]

# Google Ads Conversion ID - Update this with your actual conversion ID
GOOGLE_ADS_ID = 'AW-6127066987'
GOOGLE_ADS_LABEL = 'Checkout'  # Update with actual conversion label

# Global site tag for Google Ads
GOOGLE_GTAG = f'''<script async src="https://www.googletagmanager.com/gtag/js?id={GOOGLE_ADS_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GOOGLE_ADS_ID}');
</script>'''

# Checkout conversion event
GOOGLE_CONVERSION = f'''<script>
function gtag_report_conversion() {{
  gtag('event', 'conversion', {{
      'send_to': '{GOOGLE_ADS_ID}/{GOOGLE_ADS_LABEL}',
      'value': 29.00,
      'currency': 'USD'
  }});
}}
</script>'''

LANDING = f'''<!DOCTYPE html><html><head><title>Local Boost</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;color:white;text-align:center;padding:50px}}h1{{font-size:3rem}}.price{{font-size:2.5rem}}.btn{{background:white;color:#667eea;padding:15px 40px;border-radius:30px;text-decoration:none;font-weight:bold;display:inline-block;margin:10px}}</style>{GOOGLE_GTAG}</head><body><h1>🚀 Local Boost</h1><p>Automated Google Business Posts</p><div class="price">$29/mo</div><a href="/checkout" class="btn" onclick="gtag_report_conversion();">Get Started</a>{GOOGLE_CONVERSION}</body></html>'''

@app.route('/')
def index(): return LANDING

@app.route('/checkout')
def checkout():
    r = requests.post('https://api.stripe.com/v1/checkout/sessions', auth=(STRIPE_KEY,''),
        data={'mode':'subscription','line_items[0][price]':PRICE,'line_items[0][quantity]':'1',
              'success_url':'https://localboostus.com/success','cancel_url':'https://localboostus.com/'})
    return redirect(r.json().get('url'),302)

@app.route('/success')
def success(): return '<h1>🎉 Welcome! <a href="/login">Login to Dashboard</a></h1>'

@app.route('/login')
def login(): return '''<!DOCTYPE html><html><body style="background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;color:white;font-family:sans-serif;padding:50px;text-align:center"><h1>🔐 Login</h1><form method="post"><input name="email" type="email" placeholder="Your email" required style="padding:15px;font-size:16px;width:250px;border-radius:8px;border:none"><br><br><button style="background:white;color:#667eea;padding:15px 30px;border-radius:8px;border:none;font-weight:bold;cursor:pointer">Login</button></form></body></html>'''

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email','').strip().lower()
    c = get_customer(email)
    if c:
        return redirect(f'/dashboard?e={email}&t={make_token(email)}')
    return '<h1>❌ Email not found. <a href="/login" style="color:white">Try again</a></h1>'

@app.route('/dashboard')
def dashboard():
    e = request.args.get('e','').lower()
    t = request.args.get('t','')
    if not e or not t or make_token(e) != t:
        return redirect('/login')
    c = get_customer(e)
    if not c:
        return redirect('/login')
    return f'''<!DOCTYPE html><html><body style="font-family:-apple-system,sans-serif;max-width:600px;margin:50px auto;padding:20px"><h1>📊 Dashboard</h1><p>Welcome, {c.get("name") or c.get("email")}!</p><p>Status: <strong>Active</strong></p><hr><h2>Your Posts</h2><p>No posts yet. We'll generate posts weekly.</p><hr><a href="/connect-google">Connect Google Business →</a></body></html>'''

@app.route('/connect-google')
def connect_google():
    return '<h1>🔗 Connect Google Business Profile</h1><p>Google OAuth coming soon!</p><a href="/">← Back</a>'

@app.route('/health')
def health(): return jsonify({'status':'ok'})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000)
