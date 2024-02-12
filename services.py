from datetime import datetime, timedelta
from smtplib import SMTPException

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from mailing.models import Mailing, Log


class StileFormMixin:
    """Стилизация форм."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'


def change_status(mailing, check_time) -> None:
    if mailing.status == 'created':
        mailing.status = 'started'
        print('started')
    elif mailing.status == 'started' and mailing.stop_point <= check_time:
        mailing.status = 'completed'
        print('completed')
    mailing.save()


def change_start_point(mailing, check_time):
    if mailing.start_point < check_time:
        if mailing.period == 'daily':
            mailing.start_point += timedelta(days=1)
        elif mailing.period == 'weekly':
            mailing.start_point += timedelta(days=7)
        elif mailing.period == 'monthly':
            mailing.start_point += timedelta(days=30)
        mailing.save()


def my_job():
    print('my_job работает')
    now = datetime.now()
    now = timezone.make_aware(now, timezone.get_current_timezone())
    mailings = Mailing.objects.filter(is_active=True)
    if mailings:
        for mailing in mailings:
            change_status(mailing, now)
            if mailing.start_point <= now <= mailing.stop_point:
                for client in mailing.client.all():
                    try:
                        response = send_mail(
                            subject=mailing.message.title,
                            message=mailing.message.text,
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[client.email],
                            fail_silently=False
                        )
                        mailing_log = Log.objects.create(
                            attempt_time=mailing.start_point,
                            attempt_status=True,
                            server_response=response,
                            mailing=mailing,
                            client=client
                        )
                        mailing_log.save()
                        change_start_point(mailing, now)
                        print("mailing_log сохранен")
                    except SMTPException as error:
                        mailing_log = Log.objects.create(
                            attempt_time=mailing.start_point,
                            attempt_status=False,
                            server_response=error,
                            mailing=mailing,
                            client=client
                        )
                        mailing_log.save()
                        print(error)
    else:
        print('no mailings')


def send_new_password(email, new_password):
    send_mail(
        subject='Пароль изменен',
        message=f'Новый пароль {new_password}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email]
    )
