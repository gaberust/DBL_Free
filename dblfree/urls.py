from django.urls import path
from . import views
from .models import State
from django.utils import timezone


urlpatterns = [
    path('', views.index, name='index'),
    path('blog', views.blog, name='blog'),
    path('blog/tag/<str:tagname>', views.blog_tag, name='blog_tag'),
    path('blog/post/<slug:slug>', views.blog_post, name='blog_post'),
    path('blog/post/<slug:slug>/auth', views.blog_post_auth, name='blog_post_auth'),
    path('blog/post/<slug:slug>/auth_bypass', views.blog_post_auth_bypass, name='blog_post_auth_bypass'),
    path('write/<str:uri>', views.write, name='write'),
    path('logout', views.logout_user, name='logout'),
    path('new', views.create_post, name='create_post'),
    path('blog/post/<slug:slug>/delete', views.delete_post, name='delete_post'),
    path('blog/post/<slug:slug>/edit', views.edit_post, name='edit_post'),
    path('blog/tag/<str:tagname>/create', views.create_tag, name='create_tag'),
    path('blog/tag/<str:tagname>/delete', views.delete_tag, name='delete_tag'),
    path('about', views.about, name='about'),
    path('portfolio', views.portfolio, name='portfolio'),
    path('contact', views.contact, name='contact'),
    path('access/create', views.create_access_token, name='create_access_token'),
    path('access', views.access, name='access'),
    path('subscribe', views.subscribe, name='subscribe'),
    path('verify', views.verify_email, name='verify'),
    path('unsubscribe', views.unsubscribe, name='unsubscribe'),
    path('privacy', views.privacy, name='privacy'),
]
