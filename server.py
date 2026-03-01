#!/usr/bin/env python3
"""
Local Boost - Production Server Entry Point
"""

from systems.webhook_server import app

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=port, debug=False)
