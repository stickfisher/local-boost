"""
Local Boost - Error Handling
"""

import time

class APIError(Exception):
    def __init__(self, message, code=500):
        self.message = message
        self.code = code
        super().__init__(message)

def retry(max_attempts=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))
            return None
        return wrapper
    return decorator

USER_MESSAGES = {
    'stripe_failed': 'Payment failed',
    'email_failed': 'Email issue',
    'ai_failed': 'Using default content'
}
