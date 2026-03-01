"""
Local Boost - Monitoring & Alerts
"""

from datetime import datetime, timedelta
from pathlib import Path
import json

ALERTS_FILE = Path(__file__).parent.parent / 'data' / 'alerts.json'

class Alert:
    CRITICAL = 'critical'
    WARNING = 'warning'
    INFO = 'info'
    
    def __init__(self, level, message, metric=None):
        self.level = level
        self.message = message
        self.metric = metric
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'level': self.level,
            'message': self.message,
            'metric': self.metric,
            'timestamp': self.timestamp
        }

class Monitor:
    def __init__(self):
        self.alerts = []
        self.thresholds = {
            'mrr_zero': 0,
            'churn_rate': 0.1,
            'error_rate': 0.05
        }
    
    def check_metrics(self, stats):
        """Check metrics against thresholds"""
        new_alerts = []
        
        # MRR is zero
        if stats.get('mrr', 0) == 0:
            new_alerts.append(Alert(self.WARNING, 'MRR is zero', 'mrr'))
        
        # High churn
        total = stats.get('total', 0)
        churned = stats.get('cancelled', 0)
        if total > 0 and churned / total > self.thresholds['churn_rate']:
            new_alerts.append(Alert(self.CRITICAL, 'High churn rate', 'churn'))
        
        # No customers
        if total == 0:
            new_alerts.append(Alert(self.INFO, 'No customers yet', 'customers'))
        
        self.alerts.extend(new_alerts)
        return new_alerts
    
    def get_alerts(self, since=None):
        if since:
            return [a for a in self.alerts if a.timestamp > since]
        return self.alerts

def get_system_status():
    """Get overall system status"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from customer_db import get_stats
    
    stats = get_stats()
    monitor = Monitor()
    alerts = monitor.check_metrics(stats)
    
    return {
        'status': 'healthy' if not alerts else 'warning',
        'stats': stats,
        'alerts': [a.to_dict() for a in alerts],
        'timestamp': datetime.now().isoformat()
    }

if __name__ == '__main__':
    print(get_system_status())
