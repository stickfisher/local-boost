"""
Local Boost - Operations Dashboard v1.0
Real-time metrics and insights
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from customer_db import get_stats, get_all_customers, get_mrr
from customer_db import get_db

def get_revenue_history(days=30):
    """Get revenue for last N days"""
    conn = Path(__file__).parent.parent / 'data' / 'customers.db'
    if not conn.exists():
        return []
    
    import sqlite3
    c = sqlite3.connect(conn)
    rows = c.execute('''
        SELECT DATE(paid_at) as date, SUM(amount) as revenue
        FROM payments
        WHERE paid_at > datetime('now', '-30 days')
        GROUP BY DATE(paid_at)
        ORDER BY date
    ''').fetchall()
    c.close()
    
    return [{'date': r[0], 'revenue': r[1]} for r in rows]

def get_email_stats():
    """Get email delivery stats"""
    conn = Path(__file__).parent.parent / 'data' / 'customers.db'
    if not conn.exists():
        return {'sent': 0, 'by_type': {}}
    
    import sqlite3
    c = sqlite3.connect(conn)
    
    total = c.execute('SELECT COUNT(*) FROM email_events').fetchone()[0]
    
    by_type = c.execute('''
        SELECT event_type, COUNT(*) as c 
        FROM email_events 
        GROUP BY event_type
    ''').fetchall()
    
    c.close()
    
    return {
        'sent': total,
        'by_type': {r[0]: r[1] for r in by_type}
    }

def get_conversion_funnel():
    """Get conversion funnel"""
    stats = get_stats()
    
    return {
        'leads': stats.get('leads', 0),
        'trial': 0,
        'active': stats.get('active', 0),
        'churned': stats.get('cancelled', 0)
    }

def get_dashboard_data():
    """Get all dashboard data"""
    stats = get_stats()
    
    return {
        'generated_at': datetime.now().isoformat(),
        'revenue': {
            'mrr': stats.get('mrr', 0),
            'ltv_total': stats.get('ltv', 0),
            'avg_ltv': stats.get('ltv', 0) // max(stats.get('total', 1), 1)
        },
        'customers': {
            'total': stats.get('total', 0),
            'active': stats.get('active', 0),
            'churned': stats.get('cancelled', 0)
        },
        'funnel': get_conversion_funnel(),
        'emails': get_email_stats(),
        'health': {
            'churn_rate': stats.get('cancelled', 0) / max(stats.get('total', 1), 1),
            'arpu': stats.get('mrr', 0) // max(stats.get('active', 1), 1)
        }
    }

def render_dashboard_html():
    """Render dashboard as HTML"""
    data = get_dashboard_data()
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Local Boost Dashboard</title>
    <style>
        body {{ font-family: system-ui; padding: 20px; background: #f5f5f5; }}
        .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .big {{ font-size: 2rem; font-weight: bold; color: #667eea; }}
        .label {{ color: #666; font-size: 0.9rem; }}
        h1 {{ color: #1a1a2e; }}
    </style>
</head>
<body>
    <h1>📊 Local Boost Dashboard</h1>
    <p>Updated: {data['generated_at'][:19]}</p>
    
    <div class="grid">
        <div class="card">
            <div class="label">Monthly Revenue (MRR)</div>
            <div class="big">${data['revenue']['mrr']}</div>
        </div>
        <div class="card">
            <div class="label">Active Customers</div>
            <div class="big">{data['customers']['active']}</div>
        </div>
        <div class="card">
            <div class="label">Lifetime Revenue</div>
            <div class="big">${data['revenue']['ltv_total']}</div>
        </div>
        <div class="card">
            <div class="label">Emails Sent</div>
            <div class="big">{data['emails']['sent']}</div>
        </div>
    </div>
    
    <h2>Conversion Funnel</h2>
    <div class="grid">
        <div class="card"><div class="label">Leads</div><div class="big">{data['funnel']['leads']}</div></div>
        <div class="card"><div class="label">Trial</div><div class="big">{data['funnel']['trial']}</div></div>
        <div class="card"><div class="label">Active</div><div class="big">{data['funnel']['active']}</div></div>
        <div class="card"><div class="label">Churned</div><div class="big">{data['funnel']['churned']}</div></div>
    </div>
    
    <h2>Health Metrics</h2>
    <div class="grid">
        <div class="card">
            <div class="label">Churn Rate</div>
            <div class="big">{data['health']['churn_rate']*100:.1f}%</div>
        </div>
        <div class="card">
            <div class="label">ARPU</div>
            <div class="big">${data['health']['arpu']}</div>
        </div>
    </div>
</body>
</html>
"""
    return html

if __name__ == '__main__':
    print("=== Dashboard Data ===")
    data = get_dashboard_data()
    print(json.dumps(data, indent=2))
    
    print("\n=== HTML Preview ===")
    html = render_dashboard_html()
    print(html[:500] + "...")
