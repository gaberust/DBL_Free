from .models import Subscriber
from jwt import encode
from django.conf import settings
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.core.mail import send_mail


def dispatch_post_notification(post):
    subscribers = Subscriber.objects.filter(verified=True)
    for subscriber in subscribers:
        name = subscriber.name if subscriber.name else 'Subscriber'
        payload = {
            'action': 'unsubscribe',
            'email': subscriber.email
        }
        token = encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        unsubscribe_url = f"https://dblfree.com{reverse('unsubscribe')}?token={token}"
        message = f"Hey {name}, there's a new post on DBL Free:\n\n" \
                  f"https://dblfree.com{reverse('blog_post', kwargs={'slug': post.slug})}\n\n" \
                  f"Unsubscribe: {unsubscribe_url}"
        html_message = render_to_string('notification_email.html', {'name': name, 'post': post,
                                                                    'unsubscribe_url': unsubscribe_url})
        send_mail(f'New Post: {post.title}', message, settings.DEFAULT_FROM_EMAIL, [subscriber.email],
                  html_message=html_message, fail_silently=True)
