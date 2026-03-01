#!/usr/bin/env python3
"""
Local Boost - Production Server Entry Point
"""

import os
import sys

# Add the project root to path - CRITICAL for Render
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Also add systems folder
systems_path = os.path.join(PROJECT_ROOT, 'systems')
if systems_path not in sys.path:
    sys.path.insert(0, systems_path)

# Now import the app
from webhook_server import app

# This makes it work with: gunicorn server:app
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=port, debug=False)
