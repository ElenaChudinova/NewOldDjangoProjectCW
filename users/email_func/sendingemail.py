from django.core.mail import send_mail

from config.settings import EMAIL_HOST_USER
from send.models import MailAttempt


def send_email(subject, message, recipient_list: list, newsletter):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=EMAIL_HOST_USER,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    except Exception as E:
        er = E
        MailAttempt.objects.create(
            status_mailing_attempt=MailAttempt.Success if er == 1 else MailAttempt.Fail,
            mail_server_response=er,
            newsletter=newsletter,
        )
