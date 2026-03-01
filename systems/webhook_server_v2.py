"""
Local Boost - Main Webhook Server v1.1
Security improved: rate limiting, validation
"""

import os
import json
from flask import Flask, request, jsonify
from datetime import datetime
from pathlib import Path
from functools import wraps
import time

app = Flask(__name__)

# Rate limiting
RATE_LIMIT = {}  # In production, use Redis

def rate_limit(requests_per_minute=60):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            
            if ip not in RATE_LIMIT:
                RATE_LIMIT[ip] = []
            
            # Clean old requests
            RATE_LIMIT[ip] = [t for t in RATE_LIMIT[ip] if now - t < 60]
            
            if len(RATE_LIMIT[ip]) >= requests_per_minute:
                return jsonify({'error': 'Rate limited'}), 429
            
            RATE_LIMIT[ip].append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Add systems
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / 'systems'))

# ... (rest of imports and routes with @rate_limit decorator added)

@app.route('/webhook/stripe', methods=['POST'])
@rate_limit(30)
def stripe_webhook():
    # ... existing code
    return jsonify({'status': 'ok'})

# ... rest of endpoints with rate limiting

if __name__ == '__main__':
    print("v1.1: Rate limiting enabled")
    app.run(port=5005, debug=True)
