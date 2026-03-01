"""
Local Boost - Main Webhook Server v1.0
Integrates: Stripe + Email + Customer DB + Dashboard
"""

import os
import sys
import json
from flask import Flask, request, jsonify, send_file
from datetime import datetime
from pathlib import Path

# Setup path - this file is in systems/ folder
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

app = Flask(__name__)

# Now import from systems folder
from systems.customer_db import get_stats, get_all_customers, add_customer, update_status
from systems.stripe_integration import handle_webhook, verify_signature
from systems.email_automation import get_email, send_email
from systems.dashboard import get_dashboard_data, render_dashboard_html

# AI for content generation
OPENAI_KEY = os.getenv('OPENAI_API_KEY', '')

# ============================================
# HEALTH CHECK
# ============================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    stats = get_stats()
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'customers': stats.get('total_customers', 0),
        'mrr': stats.get('mrr', 0)
    })

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
    
    if etype == 'checkout.session.completed':
        email = data.get('customer_details', {}).get('email') or data.get('customer_email')
        if email:
            send_email(email, 'welcome')
    
    return jsonify({'received': True}), 200

# ============================================
# EMAIL ENDPOINTS
# ============================================

@app.route('/email/<email_id>', methods=['GET'])
def get_email_content(email_id):
    """Get email content by ID"""
    email = get_email(email_id)
    if email:
        return jsonify(email)
    return jsonify({'error': 'Not found'}), 404

@app.route('/email/send', methods=['POST'])
def send_email_endpoint():
    """Send an email"""
    data = request.json
    email = data.get('email')
    template = data.get('template')
    
    if not email or not template:
        return jsonify({'error': 'Missing email or template'}), 400
    
    result = send_email(email, template)
    return jsonify(result)

# ============================================
# CUSTOMER ENDPOINTS
# ============================================

@app.route('/customers', methods=['GET'])
def list_customers():
    """List all customers"""
    customers = get_all_customers()
    return jsonify({'customers': customers})

@app.route('/customers', methods=['POST'])
def add_customer_endpoint():
    """Add a new customer"""
    data = request.json
    result = add_customer(
        email=data.get('email'),
        name=data.get('name'),
        plan=data.get('plan', 'monthly')
    )
    return jsonify(result)

@app.route('/customers/<customer_id>/status', methods=['PUT'])
def update_customer_status(customer_id):
    """Update customer status"""
    data = request.json
    result = update_status(customer_id, data.get('status'))
    return jsonify(result)

# ============================================
# CONTENT GENERATION (AI)
# ============================================

@app.route('/generate-content', methods=['POST'])
def generate_content():
    """Generate social media content using AI"""
    if not OPENAI_KEY:
        return jsonify({'error': 'OPENAI_API_KEY not configured'}), 500
    
    data = request.json
    business_type = data.get('business_type', 'local business')
    topic = data.get('topic', 'general')
    
    # Use OpenAI to generate content
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"Generate 3 engaging social media posts for a {business_type}. Topic: {topic}. Keep under 280 chars each. Format as JSON array."
            }],
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# DASHBOARD
# ============================================

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Render the dashboard HTML"""
    data = get_dashboard_data()
    html = render_dashboard_html(data)
    return html

@app.route('/dashboard/data', methods=['GET'])
def dashboard_data():
    """Get dashboard data as JSON"""
    data = get_dashboard_data()
    return jsonify(data)

# ============================================
# STRIPE CHECKOUT
# ============================================

@app.route('/checkout', methods=['POST'])
def create_checkout():
    """Create a Stripe checkout session"""
    from systems.stripe_integration import create_checkout_session
    
    data = request.json
    price_id = data.get('price_id')
    
    if not price_id:
        return jsonify({'error': 'Missing price_id'}), 400
    
    try:
        url = create_checkout_session(price_id)
        return jsonify({'url': url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# LANDING PAGE
# ============================================

@app.route('/', methods=['GET'])
def landing():
    """Serve the landing page"""
    from pathlib import Path
    landing_path = Path(__file__).parent.parent / 'carrd_landing_page.html'
    if landing_path.exists():
        return send_file(landing_path)
    return jsonify({'message': 'Local Boost API', 'version': '1.0'})

@app.route('/carrd_landing_page.html')
def carrd_page():
    """Serve Carrd landing page"""
    from pathlib import Path
    return send_file(Path(__file__).parent.parent / 'carrd_landing_page.html')
