from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, BooleanField

from send.models import Client, Message, Newsletter
from users.forms import StyleFormMixin


class ClientForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Client
        fields = ("email", "name", "comment")


class ClientManagerForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Client
        fields = ("email", "name", "comment")


class MessageForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Message
        fields = ("subject_letter", "letter")


class MessageManagerForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Message
        fields = ("subject_letter", "letter")


class NewsletterForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Newsletter
        fields = (
            "message",
            "client",
            "disabling_mailings",
        )


class NewsletterManagerForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Newsletter
        fields = ("status_news_letter", "disabling_mailings")
