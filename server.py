#!/usr/bin/env python3
"""Minimal working server for Render"""

import os
import sys
from datetime import datetime
from flask import Flask, jsonify

# Add project root to path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Local Boost is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/')
def index():
    return jsonify({
        'name': 'Local Boost API',
        'version': '1.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
