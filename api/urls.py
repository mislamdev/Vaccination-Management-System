from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VaccineCampaignViewSet, BookingViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'campaigns', VaccineCampaignViewSet)
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
