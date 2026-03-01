"""
Local Boost - POD (Print on Demand) Integration
Integrates with ClearestPath POD system
"""

import os
import json
from pathlib import Path

# POD Config
POD_DIR = Path(__file__).parent.parent.parent / 'clearpath_pod_engine'
POD_DB = POD_DIR / 'data' / 'clearestpath.db'

def get_pod_designs(status=None):
    """Get designs from POD system"""
    if not POD_DB.exists():
        return []
    
    import sqlite3
    conn = sqlite3.connect(POD_DB)
    
    if status:
        rows = conn.execute('SELECT * FROM designs WHERE status = ?', (status,)).fetchall()
    else:
        rows = conn.execute('SELECT * FROM designs').fetchall()
    
    conn.close()
    return [dict(r) for r in rows]

def get_pod_stats():
    """Get POD stats"""
    if not POD_DB.exists():
        return {'designs': 0, 'published': 0}
    
    import sqlite3
    conn = sqlite3.connect(POD_DB)
    
    total = conn.execute('SELECT COUNT(*) FROM designs').fetchone()[0]
    published = conn.execute("SELECT COUNT(*) FROM designs WHERE status = 'published'").fetchone()[0]
    core = conn.execute("SELECT COUNT(*) FROM designs WHERE niche = 'CORE'").fetchone()[0]
    
    conn.close()
    
    return {
        'designs': total,
        'published': published,
        'core': core
    }

# POD Pipeline Functions
def submit_to_printify(design_id):
    """Submit design to Printify"""
    # This would call the POD worker
    return {'status': 'queued', 'design_id': design_id}

def check_etsy_status(product_id):
    """Check Etsy listing status"""
    # This would check Printify API
    return {'status': 'pending_sync', 'etsy_id': None}

# Combined Dashboard Data
def get_combined_stats():
    """Get stats from both Local Boost and POD"""
    from customer_db import get_stats as lb_stats
    from monitoring import get_system_status
    
    lb = lb_stats()
    pod = get_pod_stats()
    
    return {
        'local_boost': {
            'mrr': lb['mrr'],
            'customers': lb['active']
        },
        'pod': {
            'designs': pod['designs'],
            'published': pod['published']
        }
    }
