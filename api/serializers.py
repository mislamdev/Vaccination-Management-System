# api/serializers.py
from rest_framework import serializers
from .models import VaccineCampaign, Booking, Review
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'nid', 'specialization']  # etc.


class VaccineCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccineCampaign
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('patient', 'dose2_date')  # Automatically set


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('patient',)
