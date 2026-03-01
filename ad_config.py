"""
Day 3: Google Ads Configuration
Local Boost - Ad campaigns ready to launch
"""

# Campaign Settings
CAMPAIGNS = {
    "local_boost_grand_rapids": {
        "name": "Local Boost - Grand Rapids",
        "type": "Search",
        "budget_daily": 10,
        "keywords": [
            "google business profile",
            "google my business", 
            "local business marketing",
            "google posts for business",
            "google business optimization",
            "local seo grand rapids",
            "small business marketing grand rapids"
        ],
        "negative_keywords": ["free", "job", "resume", "how to", "guide", "tutorial"],
        "ad_copies": [
            {
                "headline_1": "Google Posts Done For You",
                "headline_2": "Save 2 Hours Every Week",
                "description": "We create custom Google Business posts every week. Just copy and paste. $29/mo",
                "cta": "Get Started"
            },
            {
                "headline_1": "Stop Wasting Time on Google",
                "headline_2": "Automated Posts for Business",
                "description": "Weekly posts created for YOUR business. More visibility, zero effort.",
                "cta": "Start Free Trial"
            },
            {
                "headline_1": "More Google Reviews",
                "headline_2": "With Weekly Google Posts",
                "description": "Consistent posting = better rankings. We handle everything.",
                "cta": "Claim Your Posts"
            }
        ],
        "location": "Grand Rapids, MI"
    }
}

TOTAL_BUDGET = 50
DAILY_LIMIT = 10

def get_tracked_url():
    return "https://localboostgr.carrd.co?utm_source=google&utm_medium=cpc&utm_campaign=local_boost"

if __name__ == "__main__":
    print("Local Boost Ad Config")
    print(f"Campaigns: {len(CAMPAIGNS)}")
    print(f"Budget: ${TOTAL_BUDGET}")
    print(f"Keywords per campaign: 7")
    print(f"Ad variants: 3")
