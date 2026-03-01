# Local Boost - Business Operating System

Automated Google Business Profile posting service. $29/month.

## 🚀 Quick Start

```bash
# Install dependencies
pip install flask openai gspread

# Run the server
cd systems
python webhook_server.py
```

## 📁 Architecture

```
local_boost/
├── systems/
│   ├── customer_db.py      # SQLite customer management
│   ├── email_automation.py # Email sequences
│   ├── stripe_integration.py # Payment processing
│   ├── webhook_server.py   # Main API server
│   ├── dashboard.py        # Metrics dashboard
│   └── ad_manager.py      # Google/Meta ads
├── data/
│   └── customers.db        # SQLite database
├── tests/
│   └── test_systems.py     # Test suite
└── README.md
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook/stripe` | POST | Stripe events |
| `/api/customers` | GET | List customers |
| `/api/stats` | GET | Revenue/stats |
| `/dashboard` | GET | Dashboard UI |
| `/api/test-email/<tpl>` | GET | Test emails |
| `/api/generate-posts` | POST | AI content |
| `/health` | GET | Health check |

## 📧 Email Sequences

1. **Welcome** (0h) - Welcome + what to expect
2. **Ask Info** (24h) - Get business details
3. **Expectations** (72h) - How to use
4. **First Content** (7d) - AI-generated posts
5. **Check-in** (14d) - How's it going?
6. **Win-back** (30d) - If cancelled

## 💰 Revenue

- **Price**: $29/month
- **Costs**: Stripe (2.9%), AgentMail (~$10/mo)
- **Profit**: ~$25/customer/month

## 🧪 Testing

```bash
python tests/test_systems.py
```

## 🔧 Configuration

Environment variables:
- `OPENAI_API_KEY` - For AI content
- `AGENTMAIL_API_KEY` - For emails
- `STRIPE_WEBHOOK_SECRET` - Stripe verification

## 📊 Metrics

- MRR (Monthly Recurring Revenue)
- Active Customers
- Churn Rate
- LTV (Lifetime Value)
- Email Open Rate
- Ad ROAS

## 🚦 Status

- [x] Customer DB
- [x] Email Sequences
- [x] Stripe Integration
- [x] Dashboard
- [x] Ad Config
- [ ] Google Ads Account
- [ ] First Customer
- [ ] Live Testing

---

Built by: Gary & Bob 🤖
