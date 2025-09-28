from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import uuid
import logging

from .models import Payment, PaymentRefund
from .serializers import (
    PaymentSerializer, PaymentInitiateSerializer,
    PaymentRefundSerializer, PaymentResponseSerializer
)
from .services import SSLCommerzPaymentService
from api.models import Booking

logger = logging.getLogger(__name__)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for payments - core payment processing only"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['post'])
    def initiate_payment(self, request):
        """Initiate payment for any booking - deprecated, use API app instead"""
        return Response(
            {'error': 'Payment initiation moved to /api/bookings/{id}/initiate_payment/'},
            status=status.HTTP_410_GONE
        )

    @csrf_exempt
    @action(detail=False, methods=['post'], permission_classes=[])
    def success(self, request):
        """Handle successful payment response from SSL Commerz"""
        serializer = PaymentResponseSerializer(data=request.data)
        if serializer.is_valid():
            payment_service = SSLCommerzPaymentService()
            payment = payment_service.process_success_response(serializer.validated_data)

            if payment:
                # Redirect to frontend success page
                frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
                return HttpResponseRedirect(f"{frontend_url}/payment/success?transaction_id={payment.transaction_id}")

        # Redirect to error page if processing fails
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        return HttpResponseRedirect(f"{frontend_url}/payment/error")

    @csrf_exempt
    @action(detail=False, methods=['post'], permission_classes=[])
    def fail(self, request):
        """Handle failed payment response from SSL Commerz"""
        serializer = PaymentResponseSerializer(data=request.data)
        if serializer.is_valid():
            payment_service = SSLCommerzPaymentService()
            payment_service.process_failure_response(serializer.validated_data)

        # Redirect to frontend failure page
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        transaction_id = request.data.get('tran_id', '')
        return HttpResponseRedirect(f"{frontend_url}/payment/failed?transaction_id={transaction_id}")

    @csrf_exempt
    @action(detail=False, methods=['post'], permission_classes=[])
    def cancel(self, request):
        """Handle cancelled payment response from SSL Commerz"""
        serializer = PaymentResponseSerializer(data=request.data)
        if serializer.is_valid():
            payment_service = SSLCommerzPaymentService()
            payment_service.process_cancel_response(serializer.validated_data)

        # Redirect to frontend cancel page
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        transaction_id = request.data.get('tran_id', '')
        return HttpResponseRedirect(f"{frontend_url}/payment/cancelled?transaction_id={transaction_id}")

    @csrf_exempt
    @action(detail=False, methods=['post'], permission_classes=[])
    def ipn(self, request):
        """Handle IPN (Instant Payment Notification) from SSL Commerz"""
        serializer = PaymentResponseSerializer(data=request.data)
        if serializer.is_valid():
            payment_service = SSLCommerzPaymentService()

            if serializer.validated_data.get('status') == 'VALID':
                payment_service.process_success_response(serializer.validated_data)
            else:
                payment_service.process_failure_response(serializer.validated_data)

            return Response({'status': 'OK'})

        return Response({'status': 'INVALID'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def request_refund(self, request, pk=None):
        """Request a refund for a payment"""
        payment = get_object_or_404(Payment, payment_id=pk, user=request.user)

        if payment.status != 'COMPLETED':
            return Response(
                {'error': 'Only completed payments can be refunded'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if refund already exists
        if hasattr(payment, 'paymentrefund'):
            return Response(
                {'error': 'Refund already requested for this payment'},
                status=status.HTTP_400_BAD_REQUEST
            )

        refund_amount = request.data.get('refund_amount', payment.amount)
        reason = request.data.get('reason', 'Customer requested refund')

        # Create refund request
        payment_service = SSLCommerzPaymentService()
        refund_response = payment_service.initiate_refund(payment, refund_amount, reason)

        if refund_response.get('status') == 'SUCCESS':
            return Response({
                'message': 'Refund request submitted successfully',
                'refund_id': refund_response.get('refund_id')
            })
        else:
            return Response(
                {'error': refund_response.get('error', 'Failed to process refund request')},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentRefundViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for payment refunds"""
    serializer_class = PaymentRefundSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PaymentRefund.objects.filter(
            payment__user=self.request.user
        ).order_by('-created_at')
