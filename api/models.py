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


class Booking(models.Model):
    class DoseStatus(models.TextChoices):
        BOOKED = "BOOKED", "Booked"
        COMPLETED = "COMPLETED", "Completed"
        PENDING = "PENDING", "Pending"

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    campaign = models.ForeignKey(VaccineCampaign, on_delete=models.CASCADE)
    dose1_date = models.DateField()
    dose2_date = models.DateField(null=True, blank=True)
    dose1_status = models.CharField(max_length=20, choices=DoseStatus.choices, default=DoseStatus.BOOKED)
    dose2_status = models.CharField(max_length=20, choices=DoseStatus.choices, default=DoseStatus.PENDING)

    def save(self, *args, **kwargs):
        # Automatically calculate the second dose date on first save
        if not self.pk and self.campaign.doses_required > 1:
            self.dose2_date = self.dose1_date + timedelta(days=self.campaign.dose_interval_days)
        super().save(*args, **kwargs)


class Review(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    campaign = models.ForeignKey(VaccineCampaign, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()  # Add validators for 1-5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
