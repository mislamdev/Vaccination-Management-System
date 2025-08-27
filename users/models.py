from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        DOCTOR = "DOCTOR", "Doctor"

    # Fields common to all users
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=Role.choices)

    # Patient-specific fields
    nid = models.CharField(max_length=20, unique=True, null=True, blank=True)
    medical_history = models.TextField(null=True, blank=True)

    # Doctor-specific fields
    specialization = models.CharField(max_length=100, null=True, blank=True)
    contact_details = models.CharField(max_length=100, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='doctors/', null=True, blank=True)
