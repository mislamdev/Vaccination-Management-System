from django.db import models
from django.conf import settings
from datetime import timedelta


class VaccineCampaign(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    doses_required = models.PositiveIntegerField(default=2)
    dose_interval_days = models.PositiveIntegerField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class PremiumService(models.Model):
    """Model for premium vaccine services - moved from payments app"""
    SERVICE_TYPES = [
        ('PRIORITY_BOOKING', 'Priority Booking'),
        ('HOME_VACCINATION', 'Home Vaccination'),
        ('EXPRESS_SERVICE', 'Express Service'),
        ('PREMIUM_VACCINE', 'Premium Vaccine Package'),
        ('VIP_CONSULTATION', 'VIP Consultation'),
    ]

    name = models.CharField(max_length=200)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(help_text="Service duration in minutes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"

    class Meta:
        ordering = ['service_type', 'price']


class Booking(models.Model):
    class DoseStatus(models.TextChoices):
        BOOKED = "BOOKED", "Booked"
        COMPLETED = "COMPLETED", "Completed"
        PENDING = "PENDING", "Pending"

    class BookingType(models.TextChoices):
        REGULAR = "REGULAR", "Regular"
        PRIORITY = "PRIORITY", "Priority"
        PREMIUM = "PREMIUM", "Premium Service"

    class PaymentStatus(models.TextChoices):
        FREE = "FREE", "Free"
        PENDING = "PENDING", "Payment Pending"
        PAID = "PAID", "Paid"

    class BookingStatus(models.TextChoices):
        PENDING_PAYMENT = "PENDING_PAYMENT", "Pending Payment"
        CONFIRMED = "CONFIRMED", "Confirmed"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    # Core booking fields
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    campaign = models.ForeignKey(VaccineCampaign, on_delete=models.CASCADE)
    dose1_date = models.DateField()
    dose2_date = models.DateField(null=True, blank=True)
    dose1_status = models.CharField(max_length=20, choices=DoseStatus.choices, default=DoseStatus.BOOKED)
    dose2_status = models.CharField(max_length=20, choices=DoseStatus.choices, default=DoseStatus.PENDING)

    # Enhanced booking fields (consolidated from both apps)
    booking_type = models.CharField(max_length=20, choices=BookingType.choices, default=BookingType.REGULAR)
    booking_status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.CONFIRMED)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.FREE)

    # Premium service fields (moved from payments app)
    premium_service = models.ForeignKey(PremiumService, on_delete=models.CASCADE, null=True, blank=True)
    scheduled_date = models.DateTimeField(null=True, blank=True, help_text="For premium services")
    address = models.TextField(null=True, blank=True, help_text="Required for home services")
    special_instructions = models.TextField(null=True, blank=True)
    priority_fee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically calculate the second dose date on first save
        if not self.pk and self.campaign.doses_required > 1:
            self.dose2_date = self.dose1_date + timedelta(days=self.campaign.dose_interval_days)

        # Auto-set booking status based on payment requirements
        if self.is_premium_booking and not self.payment_status == self.PaymentStatus.PAID:
            self.booking_status = self.BookingStatus.PENDING_PAYMENT
        elif self.payment_status == self.PaymentStatus.PAID:
            self.booking_status = self.BookingStatus.CONFIRMED

        super().save(*args, **kwargs)

    @property
    def is_priority_booking(self):
        return self.booking_type == self.BookingType.PRIORITY

    @property
    def is_premium_booking(self):
        return self.booking_type == self.BookingType.PREMIUM or self.premium_service is not None

    @property
    def requires_payment(self):
        return self.payment_status in [self.PaymentStatus.PENDING, self.PaymentStatus.PAID]

    @property
    def total_amount(self):
        """Calculate total amount for the booking"""
        amount = 0
        if self.priority_fee:
            amount += self.priority_fee
        if self.premium_service:
            amount += self.premium_service.price
        return amount

    def __str__(self):
        service_info = f" - {self.premium_service.name}" if self.premium_service else ""
        return f"Booking {self.id} - {self.patient.username} - {self.campaign.name}{service_info}"

    class Meta:
        ordering = ['-created_at']


class Review(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    campaign = models.ForeignKey(VaccineCampaign, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()  # Add validators for 1-5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
