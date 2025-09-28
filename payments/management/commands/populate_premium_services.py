from django.core.management.base import BaseCommand
from payments.models import PremiumService


class Command(BaseCommand):
    help = 'Populate database with sample premium services'

    def handle(self, *args, **options):
        premium_services = [
            {
                'name': 'Priority Vaccination Booking',
                'service_type': 'PRIORITY_BOOKING',
                'description': 'Skip the regular queue and get priority scheduling for your vaccination appointments.',
                'price': 500.00,
                'duration_minutes': 30,
            },
            {
                'name': 'Home Vaccination Service',
                'service_type': 'HOME_VACCINATION',
                'description': 'Get vaccinated in the comfort of your home with our certified medical professionals.',
                'price': 1500.00,
                'duration_minutes': 45,
            },
            {
                'name': 'Express Vaccination Package',
                'service_type': 'EXPRESS_SERVICE',
                'description': 'Fast-track vaccination service with minimal waiting time and expedited processing.',
                'price': 800.00,
                'duration_minutes': 20,
            },
            {
                'name': 'Premium Vaccine Package',
                'service_type': 'PREMIUM_VACCINE',
                'description': 'Access to premium imported vaccines with extended immunity coverage.',
                'price': 2000.00,
                'duration_minutes': 30,
            },
            {
                'name': 'VIP Medical Consultation',
                'service_type': 'VIP_CONSULTATION',
                'description': 'One-on-one consultation with specialist doctors before and after vaccination.',
                'price': 1200.00,
                'duration_minutes': 60,
            },
        ]

        created_count = 0
        for service_data in premium_services:
            service, created = PremiumService.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created premium service: {service.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Premium service already exists: {service.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} premium services')
        )
