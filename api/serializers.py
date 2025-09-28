# api/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import VaccineCampaign, Booking, Review, PremiumService
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'nid', 'specialization']


class VaccineCampaignSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = VaccineCampaign
        fields = '__all__'
        read_only_fields = ('created_by',)


class PremiumServiceSerializer(serializers.ModelSerializer):
    """Serializer for premium services - moved from payments app"""

    class Meta:
        model = PremiumService
        fields = [
            'id', 'name', 'service_type', 'description',
            'price', 'duration_minutes', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookingSerializer(serializers.ModelSerializer):
    """Enhanced booking serializer supporting all booking types"""
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    premium_service = PremiumServiceSerializer(read_only=True)
    premium_service_id = serializers.IntegerField(write_only=True, required=False)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'patient', 'patient_name', 'campaign', 'campaign_name',
            'dose1_date', 'dose2_date', 'dose1_status', 'dose2_status',
            'booking_type', 'booking_status', 'payment_status',
            'premium_service', 'premium_service_id', 'scheduled_date',
            'address', 'special_instructions', 'priority_fee',
            'total_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'patient', 'patient_name', 'campaign_name', 'dose2_date',
            'booking_status', 'total_amount', 'created_at', 'updated_at'
        ]

    def validate_premium_service_id(self, value):
        """Validate that the premium service exists and is active"""
        if value:
            try:
                service = PremiumService.objects.get(id=value, is_active=True)
                return value
            except PremiumService.DoesNotExist:
                raise serializers.ValidationError("Premium service not found or inactive")
        return value

    def validate_scheduled_date(self, value):
        """Validate that the scheduled date is in the future (for premium services)"""
        if value:
            now = timezone.now()
            if hasattr(value, 'tzinfo') and value.tzinfo is None:
                value = timezone.make_aware(value)

            if value <= now:
                raise serializers.ValidationError("Scheduled date must be in the future")
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        premium_service_id = attrs.get('premium_service_id')
        booking_type = attrs.get('booking_type', 'REGULAR')
        address = attrs.get('address')

        # If premium service is selected, set booking type appropriately
        if premium_service_id:
            attrs['booking_type'] = 'PREMIUM'

            # Check if address is required for home services
            try:
                service = PremiumService.objects.get(id=premium_service_id)
                if service.service_type == 'HOME_VACCINATION' and not address:
                    raise serializers.ValidationError({
                        'address': 'Address is required for home vaccination service'
                    })

                # Set payment status for premium services
                attrs['payment_status'] = 'PENDING'
            except PremiumService.DoesNotExist:
                pass

        # Priority booking validation
        elif booking_type == 'PRIORITY':
            priority_fee = attrs.get('priority_fee')
            if not priority_fee or priority_fee <= 0:
                raise serializers.ValidationError({
                    'priority_fee': 'Priority fee is required for priority bookings'
                })
            attrs['payment_status'] = 'PENDING'

        return attrs


class BookingCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating regular bookings"""

    class Meta:
        model = Booking
        fields = ['campaign', 'dose1_date']

    def create(self, validated_data):
        validated_data['patient'] = self.context['request'].user
        return super().create(validated_data)


class PremiumBookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating premium service bookings"""

    class Meta:
        model = Booking
        fields = [
            'campaign', 'dose1_date', 'premium_service',
            'scheduled_date', 'address', 'special_instructions'
        ]

    def validate(self, attrs):
        attrs['booking_type'] = 'PREMIUM'
        attrs['payment_status'] = 'PENDING'

        premium_service = attrs.get('premium_service')
        if premium_service and premium_service.service_type == 'HOME_VACCINATION':
            if not attrs.get('address'):
                raise serializers.ValidationError({
                    'address': 'Address is required for home vaccination service'
                })

        return attrs

    def create(self, validated_data):
        validated_data['patient'] = self.context['request'].user
        return super().create(validated_data)


class PriorityBookingUpgradeSerializer(serializers.Serializer):
    """Serializer for upgrading regular booking to priority"""
    priority_fee = serializers.DecimalField(max_digits=8, decimal_places=2)

    def validate_priority_fee(self, value):
        if value <= 0:
            raise serializers.ValidationError("Priority fee must be greater than 0")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'patient', 'patient_name', 'campaign', 'campaign_name',
            'rating', 'comment', 'created_at'
        ]
        read_only_fields = ('patient', 'patient_name', 'campaign_name', 'created_at')
