"""
Day 2: Email Sequences for Local Boost
Ready to use - just plug in AgentMail
"""

from datetime import datetime, timedelta

# ============================================
# EMAIL SEQUENCE CONFIGURATION
# ============================================

SEQUENCE_CONFIG = {
    "welcome": {
        "delay_hours": 0,
        "subject": "You're in! 🎉 Welcome to Local Boost",
        "template": "welcome"
    },
    "ask_business": {
        "delay_hours": 24,
        "subject": "Quick question about your business",
        "template": "ask_business"
    },
    "expectations": {
        "delay_hours": 72,
        "subject": "How to get the most from Local Boost",
        "template": "expectations"
    },
    "first_content": {
        "delay_hours": 168,  # 7 days
        "subject": "Your first Google posts are here!",
        "template": "first_content"
    },
    "check_in": {
        "delay_hours": 336,  # 14 days
        "subject": "How are your posts going?",
        "template": "check_in"
    },
    "win_back": {
        "delay_hours": 720,  # 30 days after cancellation
        "subject": "We miss you! Come back?",
        "template": "win_back"
    }
}

# ============================================
# EMAIL TEMPLATES
# ============================================

def get_email(template, name="there", custom_fields=None):
    """Get email template with personalization"""
    
    templates = {
        "welcome": f"""Hey {name}!

You're officially a Local Boost member! 🎉

WHAT HAPPENS NEXT:
📧 Day 1 (now): This email
📝 Day 2: I'll ask about your business
📅 Day 7: Your first content arrives!

Just reply if you have questions.

- Bob
Local Boost

---
Unsubscribe: https://localboostgr.carrd.co/unsubscribe""",

        "ask_business": f"""Hey {name}!

Quick question - what's your MAIN service or product?

For example:
- "We do residential roofing"
- "Hair salon and spa"
- "Auto repair - foreign and domestic"

Just reply with 3 words and I'll customize your content!

- Bob

---
Unsubscribe: https://localboostgr.carrd.co/unsubscribe""",

        "expectations": f"""Hey {name}!

Here's how to get the MOST from Local Boost:

✅ COPY & PASTE - Just copy what I send, paste into Google
✅ POST WEEKLY - More posts = better visibility
✅ ADD PHOTOS - Posts with images get 3x more views
✅ REPLY TO REVIEWS - Google rewards engagement

Questions? Just reply.

- Bob

---
Unsubscribe: https://localboostgr.carrd.co/unsubscribe""",

        "first_content": f"""Hey {name}!

Your first weekly Google posts are here:

---
{get_sample_posts()}
---

Just copy and paste these into your Google Business Profile!

Need anything changed? Just reply with what you'd like different.

- Bob

---
Unsubscribe: https://localboostgr.carrd.co/unsubscribe""",

        "check_in": f"""Hey {name}!

It's been 2 weeks - how are your Google posts going?

Are you:
✅ Posting every week?
✅ Adding photos?
✅ Getting more views?

Let me know if you need help!

- Bob

---
Unsubscribe: https://localboostgr.carrd.co/unsubscribe""",

        "win_back": f"""Hey {name},

We noticed you cancelled - sorry to see you go!

What could we have done better?

Reply and let us know - we'd love to have you back.

- The Local Boost Team

---
Stay subscribed: https://localboostgr.carrd.co"""
    }
    
    return templates.get(template, templates["welcome"])

def get_sample_posts():
    """Sample posts for first email"""
    return """POST 1: 🔥 Save 20% this month! Book your appointment today.

POST 2: ⭐ 5-star service guaranteed. Licensed & insured. Call now!

POST 3: Thanks for your support! We're here to help with all your needs.

POST 4: Open Monday-Friday 9am-6pm. Weekend appointments available."""

# ============================================
# AI-GENERATED CONTENT
# ============================================

def generate_ai_posts(business_type="local business", topics=None):
    """
    Generate custom posts with AI
    Returns 4 post strings
    """
    # This would call OpenAI in production
    # For now, return template
    return get_sample_posts()

# ============================================
# SEQUENCE TRACKING
# ============================================

# In production, track which email each customer received
# and when to send the next one

TRACKING_SCHEMA = {
    "customer_email": "string",
    "sequence_step": "string",  # welcome, ask_business, etc
    "last_sent": "datetime",
    "responded": "boolean",
    "response_text": "string"
}

# ============================================
# SEND FUNCTION (for webhook integration)
# ============================================

def send_sequence_email(to_email, template, name="there"):
    """Send an email from the sequence"""
    import agentmail
    
    email_body = get_email(template, name)
    subject = SEQUENCE_CONFIG.get(template, {}).get("subject", "Update from Local Boost")
    
    # This would actually send in production:
    # client.inboxes.messages.send(
    #     inbox_id=AGENTMAIL_INBOX,
    #     to=to_email,
    #     subject=subject,
    #     text=email_body
    # )
    
    print(f"Would send to {to_email}: {subject}")
    return {"sent": True, "template": template}

if __name__ == "__main__":
    # Test all templates
    print("=== EMAIL SEQUENCES ===\n")
    for template in ["welcome", "ask_business", "expectations", "first_content", "check_in", "win_back"]:
        print(f"--- {template.upper()} ---")
        print(get_email(template, "Gary"))
        print()
