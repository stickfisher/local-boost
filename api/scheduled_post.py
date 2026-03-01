"""
Scheduled post endpoint - called by Vercel Cron
"""
import os
import sys
import json
import requests
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def handler(request):
    """Called by Vercel cron every week"""
    
    OPENAI_KEY = os.getenv('OPENAI_API_KEY', '').strip()
    results = []
    
    # Get customers who need posts (in production, this would query a DB)
    customers = get_active_customers()
    
    for customer in customers:
        try:
            # Generate post using AI
            post_content = generate_post(OPENAI_KEY, customer['business_type'])
            
            # Post to Google Business Profile (when connected)
            # For now, just log what would be posted
            results.append({
                'customer': customer['email'],
                'content': post_content,
                'status': 'generated'
            })
            
        except Exception as e:
            results.append({
                'customer': customer.get('email'),
                'error': str(e)
            })
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'timestamp': datetime.now().isoformat(),
            'processed': len(customers),
            'results': results
        })
    }

def get_active_customers():
    """Get list of active customers - placeholder"""
    # In production, this would query Stripe/DB for active subs
    return []

def generate_post(api_key, business_type):
    """Generate a Google Business post using AI"""
    if not api_key:
        raise Exception("No OpenAI key")
    
    resp = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'gpt-3.5-turbo',
            'messages': [{
                'role': 'user',
                'content': f'Write a short Google Business Profile post for a {business_type}. Include relevant emojis. Keep under 150 characters. Make it engaging.'
            }],
            'max_tokens': 200
        },
        timeout=30
    )
    
    result = resp.json()
    return result['choices'][0]['message']['content']

# For local testing
if __name__ == '__main__':
    handler(None)
