# SSL Commerz Payment Gateway Integration

This document provides a comprehensive guide for the SSL Commerz payment gateway integration in the Vaccination Management System.

## Overview

The payment system supports:
- Premium vaccination services
- Priority booking upgrades
- Home vaccination services
- Express vaccination packages
- VIP medical consultations

## Setup Instructions

### 1. SSL Commerz Account Setup

1. Register at [SSL Commerz](https://sslcommerz.com/)
2. Get your Store ID and Store Password
3. Update your `.env` file with the credentials:

```env
SSLCOMMERZ_STORE_ID="your_actual_store_id"
SSLCOMMERZ_STORE_PASSWORD="your_actual_store_password"
SSLCOMMERZ_IS_SANDBOX="True"  # Set to False for production
```

### 2. Database Migration

Run the following commands to set up the database:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py populate_premium_services
```

### 3. Frontend Configuration

Update your frontend URL in the `.env` file:
```env
FRONTEND_URL="http://your-frontend-domain.com"
```

## API Endpoints

### Premium Services
- `GET /api/payments/services/` - List all premium services
- `GET /api/payments/services/?service_type=PRIORITY_BOOKING` - Filter by service type

### Premium Bookings
- `POST /api/payments/bookings/` - Create a premium service booking
- `GET /api/payments/bookings/` - List user's premium bookings
- `POST /api/payments/bookings/{id}/initiate_payment/` - Initiate payment for booking

### Payments
- `GET /api/payments/payments/` - List user's payments
- `POST /api/payments/payments/initiate_priority_payment/` - Upgrade regular booking to priority
- `POST /api/payments/payments/{id}/request_refund/` - Request payment refund

### Payment Callbacks (SSL Commerz)
- `POST /api/payments/payments/success/` - Success callback
- `POST /api/payments/payments/fail/` - Failure callback
- `POST /api/payments/payments/cancel/` - Cancel callback
- `POST /api/payments/payments/ipn/` - Instant Payment Notification

## Usage Examples

### 1. Create Premium Service Booking

```python
# Request
POST /api/payments/bookings/
{
    "premium_service_id": 1,
    "scheduled_date": "2025-10-15T10:00:00Z",
    "address": "123 Main St, Dhaka",
    "special_instructions": "Please call before arrival"
}

# Response
{
    "booking_id": "550e8400-e29b-41d4-a716-446655440000",
    "user": 1,
    "premium_service": {
        "id": 1,
        "name": "Home Vaccination Service",
        "price": "1500.00"
    },
    "status": "PENDING_PAYMENT",
    "total_amount": "1500.00"
}
```

### 2. Initiate Payment

```python
# Request
POST /api/payments/bookings/{booking_id}/initiate_payment/

# Response
{
    "payment_url": "https://sandbox.sslcommerz.com/gwprocess/v4/...",
    "transaction_id": "VAC_A1B2C3D4E5F6",
    "payment_id": "550e8400-e29b-41d4-a716-446655440001",
    "session_key": "ABC123XYZ789"
}
```

### 3. Upgrade Regular Booking to Priority

```python
# Request
POST /api/payments/payments/initiate_priority_payment/
{
    "booking_id": 123,
    "amount": "500.00",
    "customer_phone": "+8801XXXXXXXXX"
}

# Response
{
    "payment_url": "https://sandbox.sslcommerz.com/gwprocess/v4/...",
    "transaction_id": "PRI_A1B2C3D4E5F6",
    "payment_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

## Premium Service Types

1. **PRIORITY_BOOKING** - Skip regular queues (৳500)
2. **HOME_VACCINATION** - Vaccination at home (৳1500)
3. **EXPRESS_SERVICE** - Fast-track service (৳800)
4. **PREMIUM_VACCINE** - Premium imported vaccines (৳2000)
5. **VIP_CONSULTATION** - Specialist consultation (৳1200)

## Payment Flow

1. User selects premium service or priority upgrade
2. System creates booking/payment record
3. SSL Commerz payment session is initialized
4. User is redirected to SSL Commerz gateway
5. User completes payment
6. SSL Commerz redirects back with payment status
7. System verifies payment and updates booking status

## Security Features

- Transaction verification with SSL Commerz
- Secure payment URLs with session validation
- Encrypted payment data storage
- Comprehensive logging for audit trails
- CSRF protection on callback endpoints

## Error Handling

The system handles various error scenarios:
- Payment gateway timeouts
- Invalid payment amounts
- Network connectivity issues
- Transaction verification failures

## Admin Interface

Access the Django admin panel to:
- Manage premium services
- Monitor payments and transactions
- Process refund requests
- View booking analytics

## Testing

For testing in sandbox mode:
- Use test card numbers provided by SSL Commerz
- Set `SSLCOMMERZ_IS_SANDBOX=True`
- Use the sandbox credentials

## Production Deployment

1. Set `SSLCOMMERZ_IS_SANDBOX=False`
2. Use production SSL Commerz credentials
3. Configure proper SSL certificates
4. Set up monitoring for payment transactions
5. Implement backup and recovery procedures

## Support

For technical support or payment gateway issues:
- Check the payment logs in `payment.log`
- Review SSL Commerz documentation
- Contact SSL Commerz technical support for gateway issues
