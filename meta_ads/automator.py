"""
Local Boost - Meta/Facebook Ads Automator
Creates and manages Facebook/Instagram ads automatically
"""

import os
import requests
from datetime import datetime

# Facebook Marketing API
FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ADS_TOKEN', '')
FB_API_VERSION = 'v21.0'

class MetaAdsAutomator:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = f'https://graph.facebook.com/{FB_API_VERSION}'
        self.headers = {}
    
    def create_campaign(self, campaign_name, objective='CONVERSIONS', status='PAUSED'):
        """Create a new Facebook/Instagram campaign"""
        
        # For Local Boost, we'll use 'OUTCOME_TRAFFIC' or 'CONVERSIONS'
        endpoint = f'{self.base_url}/act_{self.ad_account_id}/campaigns'
        
        campaign = {
            'name': campaign_name,
            'objective': objective,  # TRAFFIC, CONVERSIONS, LEAD_GENERATION
            'status': status,  # PAUSED to start
            'special_ad_category': 'NONE'
        }
        
        return campaign
    
    def create_ad_set(self, campaign_id, name, daily_budget, targeting):
        """Create an ad set (targeting + budget)"""
        
        ad_set = {
            'campaign_id': campaign_id,
            'name': name,
            'daily_budget': daily_budget * 100,  # Cents
            'billing_event': 'IMPRESSIONS',
            'optimization_goal': 'CONVERSIONS',
            'targeting': targeting,
            'status': 'PAUSED'
        }
        
        return ad_set
    
    def create_ad_creative(self, headline, body, image_url, call_to_action):
        """Create ad creative"""
        
        creative = {
            'name': f'Ad Creative - {headline[:20]}',
            'body': body,
            'call_to_action': {
                'type': call_to_action,  # LEARN_MORE, SIGN_UP, BOOK_NOW
                'value': {'link': 'https://localboostgr.carrd.co/'}
            },
            'image_url': image_url,
            'title': headline,
            'object_url': 'https://localboostgr.carrd.co/'
        }
        
        return creative
    
    def get_targeting_grand_rapids(self):
        """Targeting for Grand Rapids local businesses"""
        
        return {
            'geo_locations': {
                'cities': [{'key': '2391585', 'name': 'Grand Rapids, MI'}]  # Grand Rapids
            },
            'age_min': 25,
            'age_max': 55,
            'interests': [
                {'id': '1003', 'name': 'Small Business'},
                {'id': '1111', 'name': 'Entrepreneurship'},
                {'id': '1138', 'name': 'Marketing'},
                {'id': '2250', 'name': 'Local Business'},
            ],
            'business_types': ['MEDIUM', 'SMALL'],
            'employmentStatuses': ['SELF_EMPLOYED', 'EMPLOYED']
        }
    
    def get_ad_variants(self):
        """Return multiple ad variants for A/B testing"""
        
        variants = [
            {
                'headline': 'Stop Doing Your Own Google Posts',
                'body': 'Save 2+ hours every week. We create custom Google Business posts for your business. Just copy and paste. Try free.',
                'cta': 'LEARN_MORE',
                'image_concept': 'Time savings / productivity'
            },
            {
                'headline': 'Google Posts Done For You - $29/mo',
                'body': 'Professional content delivered weekly. More visibility. More customers. Cancel anytime.',
                'cta': 'SIGN_UP',
                'image_concept': 'Value proposition'
            },
            {
                'headline': '50+ Grand Rapids Businesses Trust Us',
                'body': 'Join other local business owners. Weekly content handled. Grow your business.',
                'cta': 'LEARN_MORE',
                'image_concept': 'Social proof'
            },
            {
                'headline': 'Your Google Business, Updated Weekly',
                'body': 'Custom posts based on YOUR business. We do the work. You just publish.',
                'cta': 'GET_STARTED',
                'image_concept': 'Ease of use'
            }
        ]
        
        return variants

def create_local_boost_campaign(campaign_name=None, daily_budget=10):
    """Create a complete Local Boost Meta Ads campaign"""
    
    automator = MetaAdsAutomator(FACEBOOK_ACCESS_TOKEN)
    
    if not campaign_name:
        campaign_name = f"Local Boost - Grand Rapids - {datetime.now().strftime('%Y%m%d')}"
    
    # Build campaign components
    campaign = automator.create_campaign(campaign_name, objective='CONVERSIONS', status='PAUSED')
    targeting = automator.get_targeting_grand_rapids()
    ad_variants = automator.get_ad_variants()
    
    return {
        'campaign': campaign,
        'targeting': targeting,
        'ad_variants': ad_variants,
        'daily_budget': daily_budget,
        'setup_ready': True
    }

if __name__ == '__main__':
    result = create_local_boost_campaign()
    print(f"Campaign: {result['campaign']['name']}")
    print(f"Variants: {len(result['ad_variants'])}")
    print(f"Budget: ${result['daily_budget']}/day")
