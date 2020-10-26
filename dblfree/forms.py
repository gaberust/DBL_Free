from django.forms import ModelForm
from django import forms
from .models import Post, Subscriber
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import safe


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['slug', 'title', 'image', 'protected', 'password', 'tags', 'content']


class PostFormTagsUpdate(ModelForm):
    class Meta:
        model = Post
        fields = ['tags']


class ContactForm(forms.Form):
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)


class SubscribeForm(ModelForm):
    class Meta:
        model = Subscriber
        fields = ['name', 'email']
        labels = {
            'name': _('Name (Optional)'),
        }
