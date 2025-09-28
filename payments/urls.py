from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, PaymentRefundViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'refunds', PaymentRefundViewSet, basename='refund')

urlpatterns = [
    path('', include(router.urls)),
]
