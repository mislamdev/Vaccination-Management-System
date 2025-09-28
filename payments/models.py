import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Payment(models.Model):
    """Model for tracking payments"""
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]

    PAYMENT_METHOD = [
        ('SSLCOMMERZ', 'SSL Commerz'),
        ('CARD', 'Credit/Debit Card'),
        ('MOBILE_BANKING', 'Mobile Banking'),
        ('NET_BANKING', 'Net Banking'),
    ]

    payment_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    booking = models.ForeignKey('api.Booking', on_delete=models.CASCADE, null=True, blank=True)
    premium_service = models.ForeignKey('api.PremiumService', on_delete=models.CASCADE, null=True, blank=True)

    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='SSLCOMMERZ')

    # SSL Commerz specific fields
    transaction_id = models.CharField(max_length=100, unique=True)
    ssl_session_id = models.CharField(max_length=100, null=True, blank=True)
    ssl_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        if self.status == 'COMPLETED' and not self.paid_at:
            self.paid_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']


class PaymentRefund(models.Model):
    """Model for tracking refunds"""
    REFUND_STATUS = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=REFUND_STATUS, default='PENDING')
    refund_reference = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund for {self.payment.transaction_id} - {self.refund_amount}"
