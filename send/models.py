from email.message import EmailMessage
from pyexpat.errors import messages
from smtplib import SMTPException

from django.conf import settings
from django.db import models
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from redis.cluster import get_connection

from users.models import User


class Client(models.Model):
    email = models.CharField(max_length=100, verbose_name="Email Клиента", unique=True)
    id = models.AutoField(
        auto_created=True, primary_key=True, verbose_name="ID Клиента"
    )
    name = models.CharField(
        max_length=150,
        verbose_name="Ф.И.О.",
        help_text="Введите инициалы клиента",
        null=True,
        blank=True,
    )
    comment = models.TextField(
        max_length=1000,
        verbose_name="Комментарий",
        help_text="Введите комментарий о клиенте",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name} {self.name}"

    class Meta:
        verbose_name = "клиент"
        verbose_name_plural = "клиенты"
        ordering = [
            "client",
        ]
        permissions = [
            ("can_edit_email", "Can edit can edit email"),
            ("can_edit_name", "Can edit name"),
            ("can_edit_comment", "Can edit comment"),
        ]


class Message(models.Model):
    id = models.AutoField(
        auto_created=True, primary_key=True, verbose_name="ID Сообщения клиента"
    )
    subject_letter = models.CharField(
        max_length=100,
        verbose_name="Тема сообщения",
        help_text="Введите тему",
        null=True,
        blank=True,
    )
    letter = models.TextField(
        max_length=300,
        verbose_name="Текст сообщения",
        help_text="Введите текст",
        null=True,
        blank=True,
    )
    views_counter = models.PositiveIntegerField(
        verbose_name="Счетчик просмотров",
        help_text="Укажите количество просмотров",
        default=0,
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="user_message",
        blank=True,
        null=True,
        verbose_name="Владелец",
        help_text="Укажите автора письма",
    )

    def __str__(self):
        return f"{self.subject_letter} {self.letter}"

    class Meta:
        verbose_name = "письмо"
        verbose_name_plural = "письма"
        ordering = [
            "message",
        ]
        permissions = [
            ("can_edit_subject_letter", "Can edit subject_letter"),
            ("can_edit_letter", "Can edit letter"),
        ]


class Newsletter(models.Model):
    CREATED = "Создана"
    LAUNCHED = "Запущена"
    COMPLETED = "Завершена"
    STATUS_MAILING = [
        (CREATED, "Создана"),
        (LAUNCHED, "Запущена"),
        (COMPLETED, "Завершена"),
    ]
    newsletter_id = models.AutoField(
        auto_created=True, primary_key=True, verbose_name="ID Рассылки"
    )
    first_shipment = models.DateTimeField(
        editable=False,
        auto_now_add=True,
        max_length=10,
        verbose_name="Дата и время первой отправки",
        null=True,
        blank=True,
    )
    end_shipment = models.DateTimeField(
        editable=False,
        max_length=10,
        verbose_name="Дата и время окончания отправки",
        null=True,
        blank=True,
    )
    status_news_letter = models.CharField(
        max_length=100,
        choices=STATUS_MAILING,
        default=CREATED,
        verbose_name="Статус",
    )
    message = models.ForeignKey(
        Message,
        related_name="message",
        max_length=100,
        verbose_name="Сообщение",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    client = models.ManyToManyField(
        Client, related_name="client", verbose_name="Получатель"
    )

    disabling_mailings = models.BooleanField(default=False)
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="user",
        blank=True,
        null=True,
        verbose_name="Владелец",
        help_text="Укажите владельца рассылки",
    )

    def __str__(self):
        return self.status_news_letter

    class Meta:
        verbose_name = "рассылка"
        verbose_name_plural = "рассылки"
        ordering = [
            "disabling_mailings",
        ]
        permissions = [
            ("can_edit_disabling_mailings", "Сan edit disabling mailings"),
        ]


class MailAttempt(models.Model):
    Success = "Успешно"
    Fail = "Не успешно"
    STATUS_MAILING_ATTEMPT = [
        (Success, "Успешно"),
        (Fail, "Не успешно"),
    ]

    date_attempt = models.DateTimeField(
        auto_now=True,
        verbose_name="Время попытки",
    )
    status_mailing_attempt = models.CharField(
        max_length=50,
        choices=STATUS_MAILING_ATTEMPT,
        verbose_name="Статус попытки",
    )
    mail_server_response = models.TextField(
        max_length=200, verbose_name="Ответ почтового сервера"
    )
    newsletter = models.ForeignKey(
        Newsletter,
        related_name="newsletter",
        verbose_name="Рассылка",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mail_attempts",
        verbose_name="Владелец",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.status_mailing_attempt} {self.date_attempt}"

    class Meta:
        verbose_name = "попытка"
        verbose_name_plural = "попытки"


def update_status_news_letter(self):

    self.status_news_letter = "CREATED"


"""Для автоматического обновления статуса"""


def save(self, *args, **kwargs):
    self.update_status_news_letter()
    super().save(*args, **kwargs)


def send(self):
    connection = get_connection()
    for rec in self.client.all():
        email = EmailMessage(
            subject=self.messages.subject,
            body=messages.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[rec.email],
            connection=connection,
        )
    try:
        email.send()
        MailAttempt.object.create(
            mailing=self,
            status="success",
            answer_post_server="Письмо успешно отправлено",
            owner=self.owner,
        )
    except SMTPException as e:
        MailAttempt.object.create(
            mailing=self, status="Fail", answer_post_server=str(e), owner=self.owner
        )
    except Exception as e:
        MailAttempt.object.create(
            mailing=self, status="Fail", answer_post_server=str(e), owner=self.owner
        )
