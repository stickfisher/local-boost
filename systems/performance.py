"""
Local Boost - Performance & Caching
"""

from datetime import datetime
from functools import lru_cache

# In-memory cache
_cache = {'stats': None, 'timestamp': 0}
CACHE_TTL = 60  # seconds

def get_cached_stats(get_stats_fn):
    """Get stats with caching"""
    now = datetime.now().timestamp()
    
    if _cache['stats'] is None or (now - _cache['timestamp']) > CACHE_TTL:
        _cache['stats'] = get_stats_fn()
        _cache['timestamp'] = now
    
    return _cache['stats']

def clear_cache():
    """Clear all caches"""
    _cache['stats'] = None

def log_event(event_type, details):
    """Structured logging"""
    log = {
        'timestamp': datetime.now().isoformat(),
        'type': event_type,
        'details': details
    }
    print(f"LOG: {log}")

class PerformanceMonitor:
    """Monitor performance"""
    
    def __init__(self):
        self.requests = 0
        self.errors = 0
        self.start_time = datetime.now()
    
    def record_request(self):
        self.requests += 1
    
    def record_error(self):
        self.errors += 1
    
    def get_stats(self):
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            'requests': self.requests,
            'errors': self.errors,
            'uptime_seconds': uptime,
            'rpm': self.requests / max(uptime/60, 1)
        }

monitor = PerformanceMonitor()
