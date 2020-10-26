from django.core.management.base import BaseCommand
from django.utils import timezone
from dblfree.models import Subscriber


class Command(BaseCommand):
    help = 'Remove unverified subscriptions that have expired.'

    def handle(self, *args, **kwargs):
        unverified_subscriptions = Subscriber.objects.filter(verified=False)
        current_time = timezone.now()
        for subscriber in unverified_subscriptions:
            if subscriber.delete_after < current_time:
                subscriber.delete()
        self.stdout.write('Finished Subscription Cleanup.')
