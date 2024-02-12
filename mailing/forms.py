from django import forms

from mailing.models import Client, Mailing, Message
from services import StileFormMixin


class ClientForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'


class MailingForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Mailing
        fields = '__all__'


class MessageForm(StileFormMixin, forms.ModelForm):
    class Meta:
        model = Message
        fields = '__all__'
