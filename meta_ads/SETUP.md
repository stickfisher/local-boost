# Local Boost - Meta/Facebook Ads Setup

## Required Setup

### 1. Get Facebook Access Token
1. Go to https://developers.facebook.com
2. Create an app (Marketing API)
3. Get Access Token from App Dashboard
4. Or use Business Manager → Ad Accounts → Get Started

### 2. Set Environment Variable
```bash
export FACEBOOK_ADS_TOKEN=your_token_here
```

### 3. Add to Local Boost .env
```bash
echo "FACEBOOK_ADS_TOKEN=your_token_here" >> /home/gary/.openclaw/workspace/local_boost/.env
```

## What This Enables

Once configured, I can:
- Create Facebook/Instagram ad campaigns
- Generate A/B test variants
- Target local Grand Rapids businesses
- Pull performance metrics
- Optimize creative based on results

## Targeting

Current targeting:
- Location: Grand Rapids, MI (25 mi radius)
- Age: 25-55
- Interests: Small business, entrepreneurship, marketing
- Business types: Medium, Small

## Ad Creative

We test multiple variants:
- Pain-focused (time savings)
- Value proposition ($29/mo)
- Social proof (50+ businesses)
- Ease of use

