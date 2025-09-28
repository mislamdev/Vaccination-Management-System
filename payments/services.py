import logging
from decimal import Decimal

import requests
from django.conf import settings

from payments.models import Payment

logger = logging.getLogger(__name__)


class SSLCommerzPaymentService:
    """Service class for SSL Commerz payment integration using direct HTTP API"""

    def __init__(self):
        self.store_id = getattr(settings, 'SSLCOMMERZ_STORE_ID', '')
        self.store_password = getattr(settings, 'SSLCOMMERZ_STORE_PASSWORD', '')
        self.is_sandbox = getattr(settings, 'SSLCOMMERZ_IS_SANDBOX', True)

        # SSL Commerz API endpoints
        if self.is_sandbox:
            self.base_url = "https://sandbox.sslcommerz.com"
        else:
            self.base_url = "https://securepay.sslcommerz.com"

    def create_payment_session(self, payment_data):
        """
        Create a payment session with SSL Commerz using direct HTTP API

        Args:
            payment_data (dict): Payment information including amount, user details, etc.
        
        Returns:
            dict: SSL Commerz response with session URL
        """
        try:
            # Prepare SSL Commerz API data
            api_data = {
                # Store information
                'store_id': self.store_id,
                'store_passwd': self.store_password,

                # Transaction information
                'total_amount': str(payment_data['amount']),
                'currency': payment_data.get('currency', 'BDT'),
                'tran_id': payment_data['transaction_id'],

                # Product information
                'product_name': payment_data.get('product_name', 'Vaccination Service'),
                'product_category': payment_data.get('product_category', 'Healthcare'),
                'product_profile': payment_data.get('product_profile', 'health'),
                'num_of_item': str(payment_data.get('num_of_item', 1)),
                'shipping_method': payment_data.get('shipping_method', 'NO'),

                # Customer information
                'cus_name': payment_data['customer_name'],
                'cus_email': payment_data['customer_email'],
                'cus_add1': payment_data.get('customer_address', ''),
                'cus_city': payment_data.get('customer_city', 'Dhaka'),
                'cus_postcode': payment_data.get('customer_postcode', '1000'),
                'cus_country': payment_data.get('customer_country', 'Bangladesh'),
                'cus_phone': payment_data.get('customer_phone', ''),

                # URLs
                'success_url': payment_data.get('success_url'),
                'fail_url': payment_data.get('fail_url'),
                'cancel_url': payment_data.get('cancel_url'),
                'ipn_url': payment_data.get('ipn_url'),
            }

            # Make API request to SSL Commerz
            response = requests.post(
                f"{self.base_url}/gwprocess/v4/api.php",
                data=api_data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"SSL Commerz session created for transaction: {payment_data['transaction_id']}")
                return result
            else:
                logger.error(f"SSL Commerz API error: HTTP {response.status_code}")
                return {
                    'status': 'FAILED',
                    'failedreason': f'HTTP {response.status_code}: {response.text}'
                }

        except Exception as e:
            logger.error(f"Error creating SSL Commerz session: {str(e)}")
            return {'status': 'FAILED', 'failedreason': str(e)}

    def verify_payment(self, transaction_id, amount):
        """
        Verify payment status with SSL Commerz using order validation API

        Args:
            transaction_id (str): Transaction ID
            amount (Decimal): Payment amount
        
        Returns:
            dict: Payment verification response
        """
        try:
            # Prepare validation data
            validation_data = {
                'val_id': transaction_id,
                'store_id': self.store_id,
                'store_passwd': self.store_password,
                'format': 'json'
            }

            # Make validation request
            response = requests.get(
                f"{self.base_url}/validator/api/validationserverAPI.php",
                params=validation_data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()

                if result.get('status') == 'VALID' or result.get('status') == 'VALIDATED':
                    # Verify amount matches
                    paid_amount = Decimal(str(result.get('amount', 0)))
                    if paid_amount == amount:
                        return {
                            'status': 'VALID',
                            'data': result
                        }
                    else:
                        return {
                            'status': 'INVALID',
                            'error': 'Amount mismatch'
                        }

                return result
            else:
                logger.error(f"SSL Commerz validation error: HTTP {response.status_code}")
                return {'status': 'FAILED', 'error': f'HTTP {response.status_code}'}

        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return {'status': 'FAILED', 'error': str(e)}

    def process_success_response(self, response_data):
        """
        Process successful payment response from SSL Commerz
        
        Args:
            response_data (dict): Response data from SSL Commerz
        
        Returns:
            Payment: Updated payment object
        """
        try:
            transaction_id = response_data.get('tran_id')
            payment = Payment.objects.get(transaction_id=transaction_id)

            # Verify the payment with SSL Commerz
            verification = self.verify_payment(transaction_id, payment.amount)

            if verification.get('status') == 'VALID':
                payment.status = 'COMPLETED'
                payment.ssl_session_id = response_data.get('sessionkey', '')
                payment.ssl_transaction_id = response_data.get('tran_id', '')
                payment.gateway_response = response_data
                payment.save()

                # Update related booking status
                if payment.premium_service or payment.booking:
                    try:
                        # Handle both legacy PremiumBooking and new unified Booking
                        if payment.booking:
                            booking = payment.booking
                            booking.booking_status = 'CONFIRMED'
                            booking.payment_status = 'PAID'
                            booking.save()
                        else:
                            # Handle legacy PremiumBooking from payments app
                            from .models import PremiumBooking
                            premium_booking = PremiumBooking.objects.get(payment=payment)
                            premium_booking.status = 'CONFIRMED'
                            premium_booking.save()
                    except Exception as e:
                        logger.warning(f"Could not update booking status: {e}")

                logger.info(f"Payment completed successfully: {transaction_id}")
                return payment
            else:
                payment.status = 'FAILED'
                payment.gateway_response = response_data
                payment.save()
                logger.warning(f"Payment verification failed: {transaction_id}")
                return payment

        except Payment.DoesNotExist:
            logger.error(f"Payment not found for transaction: {transaction_id}")
            return None
        except Exception as e:
            logger.error(f"Error processing success response: {str(e)}")
            return None

    def process_failure_response(self, response_data):
        """
        Process failed payment response from SSL Commerz
        
        Args:
            response_data (dict): Response data from SSL Commerz
        
        Returns:
            Payment: Updated payment object
        """
        try:
            transaction_id = response_data.get('tran_id')
            payment = Payment.objects.get(transaction_id=transaction_id)

            payment.status = 'FAILED'
            payment.gateway_response = response_data
            payment.save()

            # Update related booking status
            if hasattr(payment, 'premiumbooking'):
                payment.premiumbooking.status = 'CANCELLED'
                payment.premiumbooking.save()

            logger.info(f"Payment marked as failed: {transaction_id}")
            return payment

        except Payment.DoesNotExist:
            logger.error(f"Payment not found for transaction: {transaction_id}")
            return None
        except Exception as e:
            logger.error(f"Error processing failure response: {str(e)}")
            return None

    def process_cancel_response(self, response_data):
        """
        Process cancelled payment response from SSL Commerz
        
        Args:
            response_data (dict): Response data from SSL Commerz
        
        Returns:
            Payment: Updated payment object
        """
        try:
            transaction_id = response_data.get('tran_id')
            payment = Payment.objects.get(transaction_id=transaction_id)

            payment.status = 'CANCELLED'
            payment.gateway_response = response_data
            payment.save()

            # Update related booking status
            if hasattr(payment, 'premiumbooking'):
                payment.premiumbooking.status = 'CANCELLED'
                payment.premiumbooking.save()

            logger.info(f"Payment cancelled: {transaction_id}")
            return payment

        except Payment.DoesNotExist:
            logger.error(f"Payment not found for transaction: {transaction_id}")
            return None
        except Exception as e:
            logger.error(f"Error processing cancel response: {str(e)}")
            return None

    def initiate_refund(self, payment, refund_amount, reason):
        """
        Initiate a refund request
        
        Args:
            payment (Payment): Payment object to refund
            refund_amount (Decimal): Amount to refund
            reason (str): Refund reason
        
        Returns:
            dict: Refund response
        """
        try:
            # SSL Commerz doesn't have direct refund API
            # This would typically require manual processing or third-party service
            # For now, we'll create a refund record for manual processing
            from .models import PaymentRefund

            refund = PaymentRefund.objects.create(
                payment=payment,
                refund_amount=refund_amount,
                reason=reason,
                status='PENDING'
            )

            logger.info(f"Refund request created: {refund.id} for payment: {payment.transaction_id}")
            return {
                'status': 'SUCCESS',
                'refund_id': refund.id,
                'message': 'Refund request created successfully'
            }

        except Exception as e:
            logger.error(f"Error creating refund request: {str(e)}")
            return {
                'status': 'FAILED',
                'error': str(e)
            }
