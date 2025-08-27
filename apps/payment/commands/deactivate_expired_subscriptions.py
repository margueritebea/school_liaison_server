from django.core.management.base import BaseCommand
from django.utils import timezone
from payment.models import Subscription

# Deactivate all expired subscriptions

class Command(BaseCommand):
    help = 'Deactivate all expired subscriptions'

    def handle(self, *args, **kwargs):
        now = timezone.now().date()
        expired_subscriptions = Subscription.objects.filter(end_date__lt=now, status=True)
        
        for subscription in expired_subscriptions:
            subscription.status = False
            subscription.save()

        self.stdout.write(self.style.SUCCESS(f'Deactivated {expired_subscriptions.count()} expired subscriptions'))
