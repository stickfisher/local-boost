#!/usr/bin/env python3
"""Minimal working server for Render"""

import os
import sys

# Add project root to path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

# Create app directly here (bypass import issues)
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Local Boost is running',
        'timestamp': str(datetime.now())
    })

@app.route('/')
def index():
    return jsonify({
        'name': 'Local Boost API',
        'version': '1.0'
    })

if __name__ == '__main__':
    from datetime import datetime
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
