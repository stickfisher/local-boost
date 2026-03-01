# Local Boost - Google Ads Automation Setup

## Required Setup

### 1. Get Maton API Key
1. Go to https://maton.io
2. Sign up / Log in
3. Go to API Settings
4. Copy your API key

### 2. Set Environment Variable
```bash
export MATON_API_KEY=your_key_here
```

### 3. Add to Local Boost .env
```bash
echo "MATON_API_KEY=your_key_here" >> /home/gary/.openclaw/workspace/local_boost/.env
```

### 4. Test Connection
```bash
curl -H "Authorization: Bearer $MATON_API_KEY" https://api.maton.io/v1/health
```

## What This Enables

Once configured, I can:
- Create Google Ads campaigns automatically
- Generate multiple ad variants for A/B testing
- Pull performance metrics
- Optimize bids based on results
- Scale campaigns up/down

## Cost
- Maton API: Pay per request (~$0.01 per campaign create)
- Google Ads: Your ad spend

