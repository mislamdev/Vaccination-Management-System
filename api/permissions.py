from rest_framework import permissions

from api.models import Booking


class IsDoctorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # Allow GET, HEAD, OPTIONS requests
        return request.user and request.user.is_authenticated and request.user.role == 'DOCTOR'


class CanReviewCampaign(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        campaign_id = view.kwargs.get('campaign_pk')  # Assuming nested URL
        return Booking.objects.filter(patient=request.user, campaign_id=campaign_id).exists()


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.patient == request.user
