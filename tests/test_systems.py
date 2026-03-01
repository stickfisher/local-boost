"""
Local Boost - Test Suite v1.0
Tests all systems before going live
"""

import sys
import os
from pathlib import Path

# Add systems to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'systems'))

def test_customer_db():
    """Test customer database"""
    print("\n=== TEST: Customer DB ===")
    from customer_db import init_db, add_customer, get_customer, get_stats, get_all_customers
    
    # Init
    init_db()
    print("✓ Database initialized")
    
    # Add customer
    add_customer('test@example.com', 'Test User', 'active', 'test')
    print("✓ Customer added")
    
    # Get customer
    customer = get_customer('test@example.com')
    assert customer is not None
    assert customer['email'] == 'test@example.com'
    print("✓ Customer retrieved")
    
    # Stats
    stats = get_stats()
    assert stats['total'] >= 1
    print(f"✓ Stats: {stats}")
    
    return True

def test_email_templates():
    """Test email templates render"""
    print("\n=== TEST: Email Templates ===")
    from email_automation import get_email, TEMPLATES
    
    for template in TEMPLATES:
        email = get_email(template, 'Test User')
        assert len(email) > 50
        assert 'Unsubscribe' in email
        print(f"✓ {template} template OK")
    
    return True

def test_stripe_integration():
    """Test Stripe webhook handling"""
    print("\n=== TEST: Stripe Integration ===")
    from stripe_integration import handle_webhook
    
    # Test checkout
    event = {
        'type': 'checkout.session.completed',
        'data': {
            'object': {
                'customer_email': 'new@example.com',
                'customer_details': {'name': 'New User'},
                'customer': 'cus_new',
                'subscription': 'sub_new'
            }
        }
    }
    
    result = handle_webhook(event)
    assert result['status'] == 'customer_created'
    print("✓ Checkout handled")
    
    # Test cancellation
    event = {
        'type': 'customer.subscription.deleted',
        'data': {
            'object': {
                'customer_email': 'new@example.com'
            }
        }
    }
    
    result = handle_webhook(event)
    assert result['status'] == 'cancelled'
    print("✓ Cancellation handled")
    
    return True

def test_dashboard():
    """Test dashboard data"""
    print("\n=== TEST: Dashboard ===")
    from dashboard import get_dashboard_data
    
    data = get_dashboard_data()
    assert 'revenue' in data
    assert 'customers' in data
    assert 'mrr' in data['revenue']
    print(f"✓ Dashboard data: {data['revenue']}")
    
    return True

def test_ad_manager():
    """Test ad manager"""
    print("\n=== TEST: Ad Manager ===")
    from ad_manager import get_ad_copy, AdTracker
    
    # Ad copy
    copy = get_ad_copy()
    assert 'google' in copy
    assert len(copy['google']) > 0
    print("✓ Ad copy loaded")
    
    # Tracker
    tracker = AdTracker()
    tracker.log_conversion('test', 'user@example.com', 29)
    stats = tracker.get_stats()
    assert stats['conversions'] >= 1
    print(f"✓ Ad tracker: {stats}")
    
    return True

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("LOCAL BOOST - TEST SUITE")
    print("=" * 50)
    
    tests = [
        test_customer_db,
        test_email_templates,
        test_stripe_integration,
        test_dashboard,
        test_ad_manager
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
