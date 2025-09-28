from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import PremiumService as APIPremiumService
from payments.models import PremiumService as PaymentsPremiumService


class Command(BaseCommand):
    help = 'Migrate premium services from payments app to API app'

    def handle(self, *args, **options):
        try:
            # Get all premium services from payments app
            payments_services = PaymentsPremiumService.objects.all()
            migrated_count = 0

            with transaction.atomic():
                for service in payments_services:
                    # Check if service already exists in API app
                    if not APIPremiumService.objects.filter(name=service.name).exists():
                        # Create in API app
                        APIPremiumService.objects.create(
                            name=service.name,
                            service_type=service.service_type,
                            description=service.description,
                            price=service.price,
                            duration_minutes=service.duration_minutes,
                            is_active=service.is_active,
                            created_at=service.created_at,
                            updated_at=service.updated_at
                        )
                        migrated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'Migrated premium service: {service.name}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'Premium service already exists: {service.name}')
                        )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully migrated {migrated_count} premium services to API app')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during migration: {str(e)}')
            )
