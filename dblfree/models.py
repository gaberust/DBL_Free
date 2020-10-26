from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from .utils import two_days_from_now


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    slug = models.SlugField(max_length=200, unique=True)
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    protected = models.BooleanField(default=False)
    password = models.CharField(max_length=32, blank=True)
    image = models.ImageField(upload_to='img/', default=None)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.slug


class State(models.Model):
    login_disabled_until = models.DateTimeField()
    login_url = models.CharField(max_length=32)


class Subscriber(models.Model):
    verified = models.BooleanField(default=False)
    delete_after = models.DateTimeField(default=two_days_from_now)
    name = models.CharField(max_length=32, blank=True, default='')
    email = models.EmailField(unique=True)
