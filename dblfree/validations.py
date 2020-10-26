from django.core.exceptions import ValidationError
from django.shortcuts import Http404
import functools
from django.conf import settings
import requests


def validate_page(request, page_count):
    page = request.GET.get('page')
    if page is None:
        page = 1
    try:
        page = int(page)
    except ValueError:
        raise Http404
    if page < 1 or page > page_count and page != 1:
        raise Http404
    return page


def authenticated_or_404(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not args[0].user.is_authenticated:
            raise Http404
        return func(*args, **kwargs)
    return wrapper


def validate_captcha(passcode):
    if settings.DEBUG is True:
        return
    res_body = requests.post('https://hcaptcha.com/siteverify', data={
        'secret': settings.HCAPTCHA_SECRET,
        'response': passcode
    }).json()
    if not res_body['success']:
        raise ValidationError("CAPTCHA INVALID")
