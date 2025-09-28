from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
import uuid

from .models import VaccineCampaign, Booking, Review, PremiumService
from .serializers import (
    VaccineCampaignSerializer, BookingSerializer, ReviewSerializer,
    PremiumServiceSerializer, BookingCreateSerializer,
    PremiumBookingCreateSerializer, PriorityBookingUpgradeSerializer
)
from .permissions import IsDoctorOrReadOnly, CanReviewCampaign, IsOwnerOrReadOnly

# Import payment service for SSL Commerz integration
from payments.services import SSLCommerzPaymentService
from payments.models import Payment


class VaccineCampaignViewSet(viewsets.ModelViewSet):
    queryset = VaccineCampaign.objects.all()
    serializer_class = VaccineCampaignSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsDoctorOrReadOnly]

    def perform_create(self, serializer):
        # Assign the currently logged-in doctor as the creator
        serializer.save(created_by=self.request.user)


class PremiumServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for premium services - consolidated from payments app"""
    queryset = PremiumService.objects.filter(is_active=True)
    serializer_class = PremiumServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        service_type = self.request.query_params.get('service_type')
        if service_type:
            queryset = queryset.filter(service_type=service_type)
        return queryset.order_by('price')


class BookingViewSet(viewsets.ModelViewSet):
    """Unified booking system handling all types: regular, priority, and premium"""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # Ensure users can only see their own bookings
        return Booking.objects.filter(patient=self.request.user).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'create':
            booking_type = self.request.data.get('booking_type', 'REGULAR')
            if booking_type == 'PREMIUM' or self.request.data.get('premium_service'):
                return PremiumBookingCreateSerializer
            return BookingCreateSerializer
        return BookingSerializer

    def perform_create(self, serializer):
        # Assign the currently logged-in patient
        serializer.save(patient=self.request.user)

    @action(detail=False, methods=['post'])
    def create_premium_booking(self, request):
        """Create a premium service booking"""
        serializer = PremiumBookingCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            booking = serializer.save()
            return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def upgrade_to_priority(self, request, pk=None):
        """Upgrade a regular booking to priority"""
        booking = self.get_object()

        if booking.booking_type != 'REGULAR':
            return Response(
                {'error': 'Only regular bookings can be upgraded to priority'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PriorityBookingUpgradeSerializer(data=request.data)
        if serializer.is_valid():
            booking.booking_type = 'PRIORITY'
            booking.payment_status = 'PENDING'
            booking.priority_fee = serializer.validated_data['priority_fee']
            booking.save()

            return Response(BookingSerializer(booking).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def initiate_payment(self, request, pk=None):
        """Initiate payment for booking (priority or premium)"""
        booking = self.get_object()

        if not booking.requires_payment:
            return Response(
                {'error': 'This booking does not require payment'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking.payment_status == 'PAID':
            return Response(
                {'error': 'Payment already completed for this booking'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate unique transaction ID
        transaction_id = f"VAC_{uuid.uuid4().hex[:12].upper()}"

        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            booking=booking,
            premium_service=booking.premium_service,
            amount=booking.total_amount,
            transaction_id=transaction_id,
            status='PENDING'
        )

        # Prepare payment data for SSL Commerz
        payment_service = SSLCommerzPaymentService()
        base_url = request.build_absolute_uri('/')[:-1]

        # Determine service name for payment
        if booking.booking_type == 'PREMIUM':
            service_name = booking.premium_service.name
        elif booking.booking_type == 'PRIORITY':
            service_name = f"Priority Booking - {booking.campaign.name}"
        else:
            service_name = f"Booking - {booking.campaign.name}"

        payment_data = {
            'amount': float(booking.total_amount),
            'currency': 'BDT',
            'transaction_id': transaction_id,
            'product_name': service_name,
            'product_category': 'Healthcare',
            'customer_name': request.user.get_full_name() or request.user.username,
            'customer_email': request.user.email,
            'customer_phone': getattr(request.user, 'contact_details', ''),
            'customer_address': booking.address or '',
            'success_url': f"{base_url}/api/payments/payments/success/",
            'fail_url': f"{base_url}/api/payments/payments/fail/",
            'cancel_url': f"{base_url}/api/payments/payments/cancel/",
            'ipn_url': f"{base_url}/api/payments/payments/ipn/",
        }

        # Initialize payment session
        ssl_response = payment_service.create_payment_session(payment_data)

        if ssl_response.get('status') == 'SUCCESS':
            return Response({
                'payment_url': ssl_response.get('GatewayPageURL'),
                'transaction_id': transaction_id,
                'payment_id': payment.payment_id,
                'session_key': ssl_response.get('sessionkey'),
                'booking_id': booking.id,
                'amount': booking.total_amount
            })
        else:
            payment.status = 'FAILED'
            payment.gateway_response = ssl_response
            payment.save()

            return Response(
                {'error': 'Failed to initialize payment session'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def my_payments(self, request):
        """Get all payments for the current user's bookings"""
        payments = Payment.objects.filter(user=request.user).order_by('-created_at')
        from payments.serializers import PaymentSerializer
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending_payments(self, request):
        """Get bookings with pending payments"""
        bookings = self.get_queryset().filter(
            payment_status='PENDING',
            booking_status='PENDING_PAYMENT'
        )
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def booking_stats(self, request):
        """Get booking statistics for the current user"""
        queryset = self.get_queryset()

        stats = {
            'total_bookings': queryset.count(),
            'regular_bookings': queryset.filter(booking_type='REGULAR').count(),
            'priority_bookings': queryset.filter(booking_type='PRIORITY').count(),
            'premium_bookings': queryset.filter(booking_type='PREMIUM').count(),
            'completed_bookings': queryset.filter(booking_status='COMPLETED').count(),
            'pending_payments': queryset.filter(payment_status='PENDING').count(),
            'total_spent': sum(b.total_amount for b in queryset.filter(payment_status='PAID'))
        }

        return Response(stats)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, CanReviewCampaign]

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)
