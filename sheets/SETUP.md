# Google Sheets Customer Tracker Setup

## Option 1: Service Account (Recommended)

1. Go to https://console.cloud.google.com
2. Create a new project
3. Enable Google Sheets API and Google Drive API
4. Create Service Account
5. Download JSON credentials
6. Place in `~/.google/credentials.json`

## Option 2: Environment Variable

Set `GOOGLE_CREDS_JSON` environment variable with the JSON credentials.

## Column Definitions

| Column | Description |
|--------|-------------|
| Date | When customer signed up |
| Email | Customer email |
| Name | Customer name |
| Status | active, cancelled, churned |
| MRR | Monthly recurring revenue ($29) |
| Stripe Customer ID | Customer ID from Stripe |
| Stripe Subscription ID | Subscription ID from Stripe |
| Source | How they found us |

## Usage

```python
from customer_tracker import log_customer, get_mrr

# When new customer signs up
log_customer(
    email="john@example.com",
    name="John Smith",
    status="active",
    mrr=29,
    stripe_customer_id="cus_xxx",
    stripe_sub_id="sub_xxx"
)

# Get current MRR
print(f"MRR: ${get_mrr()}")
```

