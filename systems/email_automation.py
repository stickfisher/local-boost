"""
Local Boost - Email Automation System v1.0
Complete email sequence management
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Import customer DB
import sys
sys.path.insert(0, str(Path(__file__).parent))
from customer_db import get_customer, get_all_customers, log_email_event, add_customer

# Email config
AGENTMAIL_KEY = os.getenv('AGENTMAIL_API_KEY', 'am_us_f39ceb644a239a3e5522e89d65d557515c3dac722ab78e7273936c104b217f81')
AGENTMAIL_INBOX = 'local.boost@agentmail.to'

# Email sequences
SEQUENCES = {
    'welcome': {
        'delay_hours': 0,
        'subject': "You're in! Welcome to Local Boost",
        'template': 'welcome'
    },
    'ask_business': {
        'delay_hours': 24,
        'subject': "Quick question about your business",
        'template': 'ask_info'
    },
    'expectations': {
        'delay_hours': 72,
        'subject': "How to get the most from Local Boost",
        'template': 'expectations'
    },
    'first_content': {
        'delay_hours': 168,
        'subject': "Your first Google posts are here!",
        'template': 'first_content'
    },
    'week_2_checkin': {
        'delay_hours': 336,
        'subject': "How are your posts going?",
        'template': 'checkin'
    },
    'win_back': {
        'delay_hours': 720,
        'subject': "We miss you! Come back?",
        'template': 'winback'
    }
}

TEMPLATES = {
    'welcome': """Hey {name}!

You're officially a Local Boost member!

WHAT HAPPENS NEXT:
- Day 1: This email
- Day 2: I'll ask about your business  
- Day 7: Your first content arrives

Just reply if you have questions.

- Bob
Local Boost

---
Unsubscribe: https://localboostgr.carrd.co/unsubscribe""",

    'ask_info': """Quick question - what's your MAIN service?

Just reply with:
- 3 words describing what you do
- Your top promotion (if any)

I'll customize your content!

- Bob

---
Unsubscribe""",

    'expectations': """How to get the MOST from Local Boost:

1. COPY & PASTE - Takes 2 minutes
2. POST WEEKLY - More posts = better Google ranking
3. ADD PHOTOS - 3x more views
4. REPLY TO REVIEWS - Google rewards engagement

Questions? Just reply.

- Bob

---
Unsubscribe""",

    'first_content': """Your first posts:

---
_posts_
---

Just copy & paste into your Google Business Profile!

Need changes? Reply and let me know.

- Bob

---
Unsubscribe""",

    'checkin': """Hey! It's been 2 weeks.

How are your Google posts going?

Are you:
- Posting weekly?
- Getting more views?
- Seeing more customers?

Let me know how I can help!

- Bob

---
Unsubscribe""",

    'winback': """We noticed you cancelled.

What could we have done better?

We'd love to have you back. Reply and let us know.

- The Local Boost Team

---
Stay subscribed: https://localboostgr.carrd.co"""
}

def get_email(template, name='there', custom=None):
    """Get rendered email"""
    text = TEMPLATES.get(template, TEMPLATES['welcome'])
    return text.format(name=name, **(custom or {}))

def send_email(to_email, template, name='there', custom=None):
    """Send email via AgentMail"""
    import agentmail
    
    subject = SEQUENCES.get(template, {}).get('subject', 'Update from Local Boost')
    body = get_email(template, name, custom)
    
    try:
        client = agentmail.AgentMail(api_key=AGENTMAIL_KEY)
        client.inboxes.messages.send(
            inbox_id=AGENTMAIL_INBOX,
            to=to_email,
            subject=subject,
            text=body
        )
        log_email_event(to_email, template)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def process_sequence_triggers():
    """Check who needs which email"""
    # This would run on a schedule
    # For each customer, check what emails they've received
    # and send next in sequence based on time
    pass

def test_email_sequence():
    """Test the email system"""
    print("Testing email templates...")
    for template in TEMPLATES:
        email = get_email(template, 'Gary')
        print(f"\n=== {template.upper()} ===")
        print(email[:200] + "...")
    print("\nAll templates render OK")

if __name__ == '__main__':
    test_email_sequence()
