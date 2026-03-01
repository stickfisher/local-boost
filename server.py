#!/usr/bin/env python3
"""
Local Boost - Production Server Entry Point
"""

import os
import sys

# Get absolute paths
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)
sys.path.insert(0, os.path.join(APP_DIR, 'systems'))

# Import the Flask app
from webhook_server import app, application

# For gunicorn
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=port, debug=False)
