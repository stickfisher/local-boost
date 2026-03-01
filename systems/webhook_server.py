"""
Local Boost - Main Webhook Server v1.0
Integrates: Stripe + Email + Customer DB + Dashboard
"""

import os
import json
from flask import Flask, request, jsonify, send_file
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# Add systems to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / 'systems'))

from systems.customer_db import get_stats, get_all_customers, add_customer, update_status
from systems.stripe_integration import handle_webhook, verify_signature
from systems.email_automation import get_email, send_email
from systems.dashboard import get_dashboard_data, render_dashboard_html

# AI for content generation
OPENAI_KEY = os.getenv('OPENAI_API_KEY', '')

# ============================================
# STRIPE WEBHOOK
# ============================================

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle all Stripe events"""
    payload = request.get_data()
    signature = request.headers.get('Stripe-Signature', '')
    
    # Verify (skip in dev)
    if not verify_signature(payload, signature):
        return jsonify({'error': 'Invalid signature'}), 400
    
    try:
        event = json.loads(payload)
    except:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    result = handle_webhook(event)
    
    # Trigger email based on event type
    etype = event.get('type')
    data = event.get('data', {}).get('object', {})
    email = data.get('customer_email')
    
    if email:
        customer = add_customer(email)  # Ensure exists
        
        if etype == 'checkout.session.completed':
            send_email(email, 'welcome', customer.get('name', 'there'))
            send_email(email, 'ask_info', customer.get('name', 'there'))  # Schedule next
        
        elif etype == 'invoice.payment_succeeded':
            # Send weekly content
            send_email(email, 'first_content', customer.get('name', 'there'))
        
        elif etype == 'customer.subscription.deleted':
            send_email(email, 'winback', customer.get('name', 'there'))
    
    return jsonify(result), 200

# ============================================
# CUSTOMER API
# ============================================

@app.route('/api/customers', methods=['GET'])
def list_customers():
    """List all customers"""
    status = request.args.get('status')
    return jsonify(get_all_customers(status))

@app.route('/api/customers/<email>', methods=['GET'])
def get_customer(email):
    """Get specific customer"""
    from systems.customer_db import get_customer as gc
    customer = gc(email)
    if customer:
        return jsonify(customer)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/customers', methods=['POST'])
def create_customer():
    """Manually add customer"""
    data = request.json
    return jsonify(add_customer(
        email=data['email'],
        name=data.get('name', ''),
        status=data.get('status', 'lead'),
        source=data.get('source', 'manual')
    ))

# ============================================
# STATS & DASHBOARD
# ============================================

@app.route('/api/stats')
def stats():
    """Get stats JSON"""
    return jsonify(get_stats())

@app.route('/dashboard')
def dashboard():
    """Dashboard HTML"""
    return render_dashboard_html()

# ============================================
# EMAIL TESTING
# ============================================

@app.route('/api/test-email/<template>')
def test_email(template):
    """Test send an email"""
    email = request.args.get('email', 'test@example.com')
    name = request.args.get('name', 'Test User')
    
    success = send_email(email, template, name)
    return jsonify({'sent': success, 'to': email, 'template': template})

# ============================================
# CONTENT GENERATION
# ============================================

@app.route('/api/generate-posts', methods=['POST'])
def generate_posts():
    """Generate AI posts for a business"""
    data = request.json
    business_type = data.get('business_type', 'local business')
    
    if not OPENAI_KEY:
        return jsonify({'error': 'No OpenAI key', 'posts': ['Post 1', 'Post 2']})
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user", 
                "content": f"Create 4 short Google Business posts (under 150 chars each) for a {business_type}"
            }],
            max_tokens=300
        )
        
        posts = response.choices[0].message.content
        return jsonify({'posts': posts})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# HEALTH
# ============================================

@app.route('/health')
def health():
    stats = get_stats()
    return jsonify({
        'status': 'ok',
        'mrr': stats.get('mrr', 0),
        'customers': stats.get('total', 0),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("=" * 50)
    print("Local Boost - Main Server")
    print("=" * 50)
    print(f"DB: {BASE_DIR / 'data' / 'customers.db'}")
    print(f"OpenAI: {'✓' if OPENAI_KEY else '✗'}")
    print("\nEndpoints:")
    print("  POST /webhook/stripe - Stripe events")
    print("  GET  /api/customers - List customers")
    print("  GET  /api/stats - Get stats")
    print("  GET  /dashboard - Dashboard UI")
    print("  GET  /api/test-email/<template> - Test email")
    print("  POST /api/generate-posts - AI content")
    print("\nRun: python systems/webhook_server.py")
    print("=" * 50)
    
    app.run(port=5005, debug=True)
