from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail, BadHeaderError
from dblfree.models import State
from django.conf import settings
import random
import string


class Command(BaseCommand):
    help = 'Update the login url'
    
    def handle(self, *args, **kwargs):
        new_url = ''.join((random.choice(string.ascii_letters + string.digits) for i in range(32)))
        state = State.objects.first()
        if state is None:
            State(login_disabled_until=timezone.now(), login_url=new_url).save()
        else:
            state.login_url = new_url
            state.save()
        self.stdout.write('Url Updated.')
        try:
            send_mail("DBL Free Login Url", f'https://dblfree.com/write/{new_url}', settings.DEFAULT_FROM_EMAIL,
                      [settings.CONTACT_EMAIL])
            self.stdout.write('Email Sent.')
        except BadHeaderError:
            self.stdout.write('Failed to send email.')

