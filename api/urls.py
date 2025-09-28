from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VaccineCampaignViewSet, BookingViewSet, ReviewViewSet, PremiumServiceViewSet

router = DefaultRouter()
router.register(r'campaigns', VaccineCampaignViewSet)
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'reviews', ReviewViewSet)
router.register(r'premium-services', PremiumServiceViewSet)  # Added consolidated premium services

urlpatterns = [
    path('', include(router.urls)),
]
