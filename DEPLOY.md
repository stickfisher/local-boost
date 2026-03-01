# Local Boost - Deployment Guide

## Quick Deploy (Render + Cloudflare)

### Step 1: Buy Domain on Cloudflare

1. Go to: https://dash.cloudflare.com/sign-up/registrar
2. Search: `localboost.co` or `localboostgr.com`
3. Buy: ~$8/year
4. DNS: Cloudflare provides free DNS

### Step 2: Deploy to Render

1. Go to: https://render.com
2. Connect your GitHub
3. Select: "New Web Service"
4. Connect repo: `gary/local_boost` (or wherever you push it)
5. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT server:app`
   - Environment: Python 3

6. Add Environment Variables:
   - `OPENAI_API_KEY` (your key)
   - `AGENTMAIL_API_KEY` (your key)
   - `STRIPE_WEBHOOK_SECRET` (from Stripe)

7. Deploy!

### Step 3: Connect Domain

1. In Render: Go to your service → Settings → Custom Domains
2. Add: `localboost.co` (or your domain)
3. Copy the CNAME value (something like `xxx.onrender.com`)

4. In Cloudflare DNS:
   - Type: CNAME
   - Name: @ (or localboost)
   - Value: `xxx.onrender.com`
   - Proxy: Enabled (orange cloud)

5. SSL: Automatic (Cloudflare provides)

---

## Alternative: Deploy to Railway

1. Go to: https://railway.app
2. Connect GitHub
3. New Project → Deploy from GitHub repo
4. Add env vars
5. Connect domain in Railway settings

---

## After Deploy

Update Stripe webhook:
- URL: `https://your-domain.com/webhook/stripe`

Update Carrd/landing page:
- URL: `https://your-domain.com`

---

## Cost

| Item | Cost |
|------|------|
| Domain (Cloudflare) | ~$8/year |
| Hosting (Render) | Free-$5/month |
| SSL | Free |
| Email (AgentMail) | ~$10/month |
| Stripe | 2.9% |

Total: ~$8/year + usage fees
