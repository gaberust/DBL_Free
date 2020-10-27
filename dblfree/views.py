from csp.decorators import csp_exempt
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect, reverse, HttpResponse, Http404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.template.loader import render_to_string

from .forms import PostForm, PostFormTagsUpdate, ContactForm, SubscribeForm
from .models import Post, Tag, State, Subscriber
from math import ceil

from .notifications import dispatch_post_notification
from .validations import validate_page, authenticated_or_404, validate_captcha
from django.core.mail import send_mail, BadHeaderError
from jwt import encode, decode, ExpiredSignatureError
from datetime import timedelta, datetime
from django.utils import timezone
from django.conf import settings

# Create your views here.

PAGE_SIZE = 3
ALL_ACCESS_KEY = 'ALL/ACCESS'


def index(request):
    taglist = Tag.objects.all()
    posts = Post.objects.order_by('-date_posted')[:6]
    return render(request, 'index.html', {'taglist': taglist, 'posts': posts})


def blog(request):
    page_count = ceil(Post.objects.all().count() / PAGE_SIZE)

    page = validate_page(request, page_count)

    posts = Post.objects.order_by('-date_posted')[(page - 1) * PAGE_SIZE: page * PAGE_SIZE]

    taglist = Tag.objects.all()
    return render(request, 'blog.html',
                  {'taglist': taglist, 'posts': posts, 'page': page, 'page_count': page_count,
                   'pagination_url': reverse('blog')})


def blog_tag(request, tagname):
    taglist = Tag.objects.all()
    tag = get_object_or_404(Tag, name=tagname)

    page_count = ceil(Post.objects.filter(tags__in=[tag]).count() / PAGE_SIZE)

    page = validate_page(request, page_count)

    posts = Post.objects.filter(tags__in=[tag]).order_by('-date_posted')[(page - 1) * PAGE_SIZE: page * PAGE_SIZE]
    return render(request, 'blog.html',
                  {'taglist': taglist, 'posts': posts, 'page': page, 'page_count': page_count, 'title': tag.name,
                   'pagination_url': reverse('blog_tag', kwargs={'tagname': tagname})})


def blog_post(request, slug):
    taglist = Tag.objects.all()
    post = get_object_or_404(Post, slug=slug)

    accessible = (not post.protected) or (slug in request.session) or (ALL_ACCESS_KEY in request.session)
    return render(request, 'post.html',
                  {'taglist': taglist, 'post': post, 'accessible': accessible,
                   'HYVOR_TALK_WEBSITE': settings.HYVOR_TALK_WEBSITE})


def blog_post_auth(request, slug):
    if request.method == 'POST':
        post = get_object_or_404(Post, slug=slug)
        if post.protected and request.POST.get('password') == post.password:
            request.session[slug] = True
        return redirect('blog_post', slug=slug)
    raise Http404


@authenticated_or_404
def blog_post_auth_bypass(request, slug):
    request.session[slug] = True
    return redirect('blog_post', slug=slug)


def write(request, uri):
    state = get_object_or_404(State, login_url=uri)
    if request.user.is_authenticated:
        return redirect('index')
    taglist = Tag.objects.all()
    if timezone.now() < state.login_disabled_until:
        return render(request, 'message.html', {'taglist': taglist, 'message': 'Logging in is currently not allowed.'})
    if request.method == "GET":
        return render(request, 'login.html', {'taglist': taglist, 'uri': uri, 'form': AuthenticationForm()})
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('index')
        state.login_disabled_until = timezone.now() + timedelta(seconds=60)
        state.save()
        return redirect('write', uri=uri)


@authenticated_or_404
def logout_user(request):
    if not request.user.is_authenticated:
        raise Http404
    logout(request)
    return redirect('index')


@authenticated_or_404
@csp_exempt
def create_post(request):
    taglist = Tag.objects.all()
    if request.method == "GET":
        return render(request, 'new.html', {'taglist': taglist, 'form': PostForm()})
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            for tagname in form.cleaned_data.get('tags'):
                post.tags.add(taglist.get(name=tagname))
            post.save()
            dispatch_post_notification(post)
            return redirect('blog_post', slug=post.slug)
        else:
            return render(request, 'new.html', {'taglist': taglist, 'form': form})


@authenticated_or_404
def create_tag(request, tagname):
    if request.method == 'POST':
        Tag(name=tagname).save()
        return HttpResponse(PostFormTagsUpdate())
    raise Http404


@authenticated_or_404
def delete_post(request, slug):
    if request.method == 'POST':
        post = get_object_or_404(Post, slug=slug)
        post.delete()
        return redirect('index')
    raise Http404


@authenticated_or_404
def delete_tag(request, tagname):
    if request.method == 'POST':
        tag = get_object_or_404(Tag, name=tagname)
        tag.delete()
        return redirect('index')
    raise Http404


@authenticated_or_404
@csp_exempt
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    taglist = Tag.objects.all()
    if request.method == "GET":
        return render(request, 'edit.html', {'taglist': taglist, 'slug': slug, 'form': PostForm(instance=post)})
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            post.tags.clear()
            for tagname in form.cleaned_data.get('tags'):
                post.tags.add(taglist.get(name=tagname))
            post.save()
            return redirect('blog_post', slug=post.slug)
        else:
            return render(request, 'edit.html', {'taglist': taglist, 'slug': slug, 'form': form})


def about(request):
    taglist = Tag.objects.all()
    return render(request, 'about.html', {'taglist': taglist})


def portfolio(request):
    taglist = Tag.objects.all()
    return render(request, 'portfolio.html', {'taglist': taglist})


def contact(request):
    taglist = Tag.objects.all()
    success = False
    failure = False
    captcha_failure = False
    form = None
    if request.method == 'GET':
        form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            final_message = f'From DBL Free Contact Form:\nName: {name}\nEmail: {email}\n\n{message}'
            try:
                validate_captcha(request.POST['h-captcha-response'])
                send_mail(f'Contact Form: {subject}', f'Name: {name}\nEmail: {email}\n\n{message}',
                          settings.DEFAULT_FROM_EMAIL, [settings.CONTACT_EMAIL])
                success = True
                form = ContactForm()
            except (ValidationError, KeyError) as e:
                captcha_failure = True
            except (BadHeaderError, ValueError) as e:
                failure = True
    return render(request, 'contact.html', {'taglist': taglist, 'form': form, 'success': success, 'failure': failure,
                                            'captcha_failure': captcha_failure,
                                            'HCAPTCHA_SITEKEY': settings.HCAPTCHA_SITEKEY})


@authenticated_or_404
def create_access_token(request):
    if request.method == 'POST':
        taglist = Tag.objects.all()
        payload = {
            'action': 'access',
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        message = f"https://dblfree.com{reverse('access')}?token={token}"
        return render(request, 'message.html', {'taglist': taglist, 'message': message})
    raise Http404


def access(request):
    message = ''
    try:
        payload = decode(request.GET['token'], settings.SECRET_KEY, algorithms=['HS256'])
        if payload['action'] == 'access':
            request.session[ALL_ACCESS_KEY] = True
            message = "Access to all posts has been enabled on this device."
        else:
            raise ValueError
    except ExpiredSignatureError:
        message = "Unable to process request. Reason: Link Expired."
    except:
        raise Http404
    taglist = Tag.objects.all()
    return render(request, 'message.html', {'taglist': taglist, 'message': message})


def subscribe(request):
    taglist = Tag.objects.all()
    success = False
    failure = False
    captcha_failure = False
    privacy_policy_message = False
    email_exists_unverified = False
    form = None
    if request.method == 'GET':
        form = SubscribeForm()
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            try:
                validate_captcha(request.POST['h-captcha-response'])
                to_email = form.cleaned_data['email']
                name = form.cleaned_data.get('name')
                name = name if name else 'Subscriber'
                payload = {
                    'action': 'verify',
                    'email': to_email,
                    'exp': datetime.utcnow() + timedelta(hours=48)
                }
                token = encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
                verification_url = f"https://dblfree.com{reverse('verify')}?token={token}"
                form.save()
                success = True
                form = SubscribeForm()
                message = f'Hi {name}, Please Verify Your Email Address for DBL Free:\n\n{verification_url}'
                html_message = render_to_string('verification_email.html',
                                                {'name': name, 'verification_url': verification_url})
                send_mail('Email Verification', message, settings.DEFAULT_FROM_EMAIL, [to_email],
                          html_message=html_message)
            except (ValidationError, KeyError) as e:
                captcha_failure = True
            except (BadHeaderError, ValueError) as e:
                failure = True
        else:
            subscriber = Subscriber.objects.get(email=form.cleaned_data.get('email'))
            if (subscriber is not None) and (not subscriber.verified):
                email_exists_unverified = True
                try:
                    validate_captcha(request.POST['h-captcha-response'])
                    name = subscriber.name if subscriber.name else 'Subscriber'
                    payload = {
                        'action': 'verify',
                        'email': subscriber.email,
                        'exp': datetime.utcnow() + timedelta(hours=48)
                    }
                    token = encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
                    verification_url = f"https://dblfree.com{reverse('verify')}?token={token}"
                    message = f'Hi {name}, Please Verify Your Email Address for DBL Free:\n\n{verification_url}'
                    html_message = render_to_string('verification_email.html',
                                                    {'name': name, 'verification_url': verification_url})
                    send_mail('Email Verification', message, settings.DEFAULT_FROM_EMAIL, [subscriber.email],
                              html_message=html_message)
                    form = SubscribeForm()
                except (ValidationError, KeyError) as e:
                    captcha_failure = True
                except (BadHeaderError, ValueError) as e:
                    failure = True
    return render(request, 'subscribe.html', {'taglist': taglist, 'form': form, 'success': success, 'failure': failure,
                                              'privacy_policy_message': privacy_policy_message,
                                              'captcha_failure': captcha_failure,
                                              'email_exists_unverified': email_exists_unverified,
                                              'HCAPTCHA_SITEKEY': settings.HCAPTCHA_SITEKEY})


def verify_email(request):
    message = ''
    try:
        payload = decode(request.GET['token'], settings.SECRET_KEY, algorithms=['HS256'])
        if payload['action'] == 'verify':
            subscriber = Subscriber.objects.get(email=payload['email'])
            if subscriber is None:
                raise ExpiredSignatureError
            subscriber.verified = True
            subscriber.save()
            name = subscriber.name
            name = name if name else 'Subscriber'
            message = f'Thanks for verifying your email address, {name}. ' + \
                      'You are now able to receive email notifications.'
        else:
            raise ValueError
    except ExpiredSignatureError:
        message = "Unable to process request. Reason: Link Expired."
    except:
        raise Http404
    taglist = Tag.objects.all()
    return render(request, 'message.html', {'taglist': taglist, 'message': message})


def unsubscribe(request):
    message = ''
    try:
        payload = decode(request.GET['token'], settings.SECRET_KEY, algorithms=['HS256'])
        if payload['action'] == 'unsubscribe':
            subscriber = Subscriber.objects.get(email=payload['email'])
            if subscriber is None:
                raise ExpiredSignatureError
            subscriber.delete()
            message = "Unsubscribed Successfully."
        else:
            raise ValueError
    except ExpiredSignatureError:
        message = "Unable to process request. Reason: Link Expired."
    except:
        raise Http404
    taglist = Tag.objects.all()
    return render(request, 'message.html', {'taglist': taglist, 'message': message})


def privacy(request):
    taglist = Tag.objects.all()
    return render(request, 'privacy.html', {'taglist': taglist})
