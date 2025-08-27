from django.contrib import admin

from .models import VaccineCampaign, Booking, Review

admin.site.register(VaccineCampaign)
admin.site.register(Booking)
admin.site.register(Review)
