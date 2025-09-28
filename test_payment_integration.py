"""
Test script to validate SSL Commerz payment integration
Run this script to test the payment system functionality
"""

import os
import django
import sys
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Vaccination_Management_System.settings')
django.setup()

from django.contrib.auth import get_user_model
from payments.models import PremiumService, PremiumBooking, Payment
from payments.services import SSLCommerzPaymentService
from api.models import VaccineCampaign, Booking

User = get_user_model()

def test_payment_integration():
    """Test the payment integration components"""
    print("🧪 Testing SSL Commerz Payment Integration")
    print("=" * 50)
    
    # Test 1: Check if premium services exist
    print("1. Checking Premium Services...")
    services = PremiumService.objects.filter(is_active=True)
    if services.exists():
        print(f"   ✅ Found {services.count()} premium services")
        for service in services[:3]:
            print(f"   - {service.name}: ৳{service.price}")
    else:
        print("   ❌ No premium services found. Run: python manage.py populate_premium_services")
        return False
    
    # Test 2: Check SSL Commerz configuration
    print("\n2. Checking SSL Commerz Configuration...")
    from django.conf import settings
    
    store_id = getattr(settings, 'SSLCOMMERZ_STORE_ID', '')
    store_password = getattr(settings, 'SSLCOMMERZ_STORE_PASSWORD', '')
    is_sandbox = getattr(settings, 'SSLCOMMERZ_IS_SANDBOX', True)
    
    if store_id and store_password:
        print(f"   ✅ SSL Commerz configured")
        print(f"   - Store ID: {store_id[:10]}...")
        print(f"   - Sandbox Mode: {is_sandbox}")
    else:
        print("   ⚠️  SSL Commerz credentials not configured in .env file")
        print("   Please update SSLCOMMERZ_STORE_ID and SSLCOMMERZ_STORE_PASSWORD")
    
    # Test 3: Test payment service initialization
    print("\n3. Testing Payment Service...")
    try:
        payment_service = SSLCommerzPaymentService()
        print("   ✅ SSL Commerz payment service initialized successfully")
    except Exception as e:
        print(f"   ❌ Payment service initialization failed: {e}")
        return False
    
    # Test 4: Check database models
    print("\n4. Checking Database Models...")
    try:
        # Check if models are properly migrated
        Payment.objects.count()
        PremiumBooking.objects.count()
        print("   ✅ Payment models are properly migrated")
    except Exception as e:
        print(f"   ❌ Database models not properly migrated: {e}")
        print("   Please run: python manage.py migrate")
        return False
    
    # Test 5: Create test user and booking (if possible)
    print("\n5. Testing Model Creation...")
    try:
        # Create test user if doesn't exist
        test_user, created = User.objects.get_or_create(
            username='test_payment_user',
            defaults={
                'email': 'test@example.com',
                'role': 'PATIENT'
            }
        )
        
        # Create test premium booking
        service = services.first()
        from datetime import datetime, timedelta
        
        booking = PremiumBooking.objects.create(
            user=test_user,
            premium_service=service,
            scheduled_date=datetime.now() + timedelta(days=7),
            address="Test Address, Dhaka",
            special_instructions="Test booking"
        )
        
        print(f"   ✅ Test premium booking created: {booking.booking_id}")
        
        # Clean up test data
        booking.delete()
        if created:
            test_user.delete()
            
    except Exception as e:
        print(f"   ❌ Model creation test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Payment Integration Test Complete!")
    print("\nNext Steps:")
    print("1. Update SSL Commerz credentials in .env file")
    print("2. Run migrations: python manage.py migrate")
    print("3. Populate services: python manage.py populate_premium_services")
    print("4. Test payment flow through API endpoints")
    print("5. Configure frontend payment redirects")
    
    return True

if __name__ == "__main__":
    test_payment_integration()
