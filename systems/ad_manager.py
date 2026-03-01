"""
Local Boost - Ad Platform Manager v1.0
Google Ads & Meta Ads integration
"""

import os
import json
from datetime import datetime
from pathlib import Path

# Ad Config Storage
ADS_CONFIG_FILE = Path(__file__).parent.parent / 'data' / 'ad_config.json'

def load_config():
    if ADS_CONFIG_FILE.exists():
        return json.loads(ADS_CONFIG_FILE.read_text())
    return {}

def save_config(config):
    ADS_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ADS_CONFIG_FILE.write_text(json.dumps(config, indent=2))

# ============================================
# GOOGLE ADS
# ============================================

GOOGLE_ADS_CONFIG = {
    'campaigns': {
        'local_boost_search': {
            'name': 'Local Boost - Search',
            'type': 'SEARCH',
            'status': 'PAUSED',
            'budget': 10.00,  # daily
            'keywords': [
                'google business profile',
                'google my business',
                'local business marketing',
                'google posts for business',
                'local seo service',
                'small business marketing grand rapids'
            ],
            'negative_keywords': [
                'free', 'job', 'resume', 'how to', 'guide', 'tutorial'
            ],
            'ad_copies': [
                {
                    'headlines': [
                        'Google Posts Done For You',
                        'Save 2 Hours Every Week',
                        'Grand Rapids Businesses'
                    ],
                    'descriptions': [
                        'We create custom Google Business posts every week. Just copy and paste.',
                        '$29/month. Cancel anytime. 30-day guarantee.'
                    ]
                },
                {
                    'headlines': [
                        'Stop Wasting Time on Google',
                        'Automated Posts for Business',
                        '$29/Month'
                    ],
                    'descriptions': [
                        'Weekly posts created for YOUR business. More visibility, zero effort.',
                        'Proven to increase Google visibility.'
                    ]
                }
            ]
        }
    },
    'targeting': {
        'locations': ['Grand Rapids, MI', 'Detroit, MI'],
        'radius_miles': 25
    }
}

# ============================================
# META/FACEBOOK ADS
# ============================================

META_ADS_CONFIG = {
    'campaigns': {
        'local_boost_awareness': {
            'name': 'Local Boost - Awareness',
            'type': 'AWARENESS',
            'status': 'PAUSED',
            'budget': 10.00,
            'placements': ['facebook', 'instagram'],
            'targeting': {
                'locations': ['US', 'MI'],
                'interests': ['Small Business', 'Local Marketing', 'Entrepreneurship']
            },
            'ad_copies': [
                {
                    'headline': 'Save 2 Hours Every Week',
                    'text': 'We handle your Google Business posts. You just copy and paste. More visibility, zero effort.',
                    'link_description': 'LocalBoostGR.com'
                }
            ]
        }
    }
}

# ============================================
# AD TRACKING
# ============================================

class AdTracker:
    def __init__(self):
        self.config = load_config()
    
    def log_impression(self, campaign, ad_id):
        if 'impressions' not in self.config:
            self.config['impressions'] = {}
        if campaign not in self.config['impressions']:
            self.config['impressions'][campaign] = []
        self.config['impressions'][campaign].append({
            'ad_id': ad_id,
            'timestamp': datetime.now().isoformat()
        })
        save_config(self.config)
    
    def log_click(self, campaign, ad_id, url):
        if 'clicks' not in self.config:
            self.config['clicks'] = {}
        if campaign not in self.config['clicks']:
            self.config['clicks'][campaign] = []
        self.config['clicks'][campaign].append({
            'ad_id': ad_id,
            'url': url,
            'timestamp': datetime.now().isoformat()
        })
        save_config(self.config)
    
    def log_conversion(self, campaign, email, value=29):
        if 'conversions' not in self.config:
            self.config['conversions'] = []
        self.config['conversions'].append({
            'campaign': campaign,
            'email': email,
            'value': value,
            'timestamp': datetime.now().isoformat()
        })
        save_config(self.config)
    
    def get_stats(self, campaign=None):
        stats = {
            'impressions': 0,
            'clicks': 0,
            'conversions': 0,
            'spend': 0,
            'ctr': 0,
            'cpc': 0,
            'cpa': 0
        }
        
        impressions = len(self.config.get('impressions', {}).get(campaign or 'all', []))
        clicks = len(self.config.get('clicks', {}).get(campaign or 'all', []))
        conversions = len([c for c in self.config.get('conversions', []) 
                         if campaign is None or c.get('campaign') == campaign])
        
        spend = conversions * 29  # Approximate
        
        stats = {
            'impressions': impressions,
            'clicks': clicks,
            'conversions': conversions,
            'spend': spend,
            'ctr': (clicks / impressions * 100) if impressions else 0,
            'cpc': (spend / clicks) if clicks else 0,
            'cpa': (spend / conversions) if conversions else 0
        }
        
        return stats

def get_ad_copy():
    """Get ad copy for testing"""
    return {
        'google': GOOGLE_ADS_CONFIG['campaigns']['local_boost_search']['ad_copies'],
        'meta': META_ADS_CONFIG['campaigns']['local_boost_awareness']['ad_copies']
    }

if __name__ == '__main__':
    print("=== Ad Platform Config ===")
    print(f"Google: {len(GOOGLE_ADS_CONFIG['campaigns'])} campaigns")
    print(f"Meta: {len(META_ADS_CONFIG['campaigns'])} campaigns")
    print(f"\nGoogle Keywords: {len(GOOGLE_ADS_CONFIG['campaigns']['local_boost_search']['keywords'])}")
    print("\nSample Ad:")
    print(json.dumps(GOOGLE_ADS_CONFIG['campaigns']['local_boost_search']['ad_copies'][0], indent=2))
