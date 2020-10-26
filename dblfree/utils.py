from django.utils import timezone
from datetime import timedelta


def two_days_from_now():
    return timezone.now() + timedelta(hours=48)
