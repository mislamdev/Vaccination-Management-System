from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Payment, PaymentRefund
from api.models import Booking

User = get_user_model()


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment transactions"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'payment_id', 'user', 'user_name', 'user_email',
            'booking', 'premium_service',
            'amount', 'currency', 'status', 'payment_method',
            'transaction_id', 'ssl_session_id', 'ssl_transaction_id',
            'created_at', 'updated_at', 'paid_at'
        ]
        read_only_fields = [
            'payment_id', 'user', 'user_name', 'user_email',
            'status', 'ssl_session_id', 'ssl_transaction_id',
            'created_at', 'updated_at', 'paid_at'
        ]


class PaymentInitiateSerializer(serializers.Serializer):
    """Serializer for initiating payments"""
    booking_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='BDT')
    customer_phone = serializers.CharField(max_length=20, required=False)
    customer_address = serializers.CharField(max_length=500, required=False)
    customer_city = serializers.CharField(max_length=100, default='Dhaka')
    customer_postcode = serializers.CharField(max_length=10, default='1000')
    
    def validate_booking_id(self, value):
        """Validate regular booking exists"""
        try:
            Booking.objects.get(id=value)
            return value
        except Booking.DoesNotExist:
            raise serializers.ValidationError("Booking not found")


class PaymentRefundSerializer(serializers.ModelSerializer):
    """Serializer for payment refunds"""
    payment_transaction_id = serializers.CharField(source='payment.transaction_id', read_only=True)
    user_name = serializers.CharField(source='payment.user.get_full_name', read_only=True)
    
    class Meta:
        model = PaymentRefund
        fields = [
            'id', 'payment', 'payment_transaction_id', 'user_name',
            'refund_amount', 'reason', 'status', 'refund_reference',
            'created_at', 'processed_at'
        ]
        read_only_fields = [
            'id', 'payment_transaction_id', 'user_name',
            'status', 'refund_reference', 'created_at', 'processed_at'
        ]


class PaymentResponseSerializer(serializers.Serializer):
    """Serializer for SSL Commerz response handling"""
    status = serializers.CharField()
    tran_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    currency = serializers.CharField(required=False)
    sessionkey = serializers.CharField(required=False)
    tran_date = serializers.CharField(required=False)
    val_id = serializers.CharField(required=False)
    card_type = serializers.CharField(required=False)
    card_no = serializers.CharField(required=False)
    bank_tran_id = serializers.CharField(required=False)
    card_issuer = serializers.CharField(required=False)
    card_brand = serializers.CharField(required=False)
    card_issuer_country = serializers.CharField(required=False)
    card_issuer_country_code = serializers.CharField(required=False)
    verify_sign = serializers.CharField(required=False)
    verify_key = serializers.CharField(required=False)
    verify_sign_sha2 = serializers.CharField(required=False)
    currency_type = serializers.CharField(required=False)
    currency_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    currency_rate = serializers.DecimalField(max_digits=10, decimal_places=6, required=False)
    base_fair = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    value_a = serializers.CharField(required=False)
    value_b = serializers.CharField(required=False)
    value_c = serializers.CharField(required=False)
    value_d = serializers.CharField(required=False)
    risk_level = serializers.CharField(required=False)
    risk_title = serializers.CharField(required=False)
