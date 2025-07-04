from django.urls import path

from send.apps import SendConfig
from send.views import (
    HomePageView,
    ClientCreateView,
    ClientUpdateView,
    ClientDeleteView,
    MessageCreateView,
    MessageUpdateView,
    MessageDeleteView,
    ClientView,
    MessageListView,
    NewsletterListView,
    AttemptsListView,
    NewsletterCreateView,
    SendNewsLetterList,
    NewsLetterDetailView,
    NewsletterUpdateView,
    NewsletterDeleteView,
)

app_name = SendConfig.name

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("client/create/", ClientCreateView.as_view(), name="client_create"),
    path("client/", ClientView.as_view(), name="client_list"),
    path("client/<int:pk>/update/", ClientUpdateView.as_view(), name="client_update"),
    path("client/<int:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),
    path("message/", MessageListView.as_view(), name="message_list"),
    path("message/create/", MessageCreateView.as_view(), name="message_create"),
    path(
        "message/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"
    ),
    path(
        "message/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
    path("newsletter/", NewsletterListView.as_view(), name="newsletter_list"),
    path(
        "newsletter/<int:pk>/update",
        NewsletterUpdateView.as_view(),
        name="newsletter_update",
    ),
    path(
        "newsletter/<int:pk>/delete",
        NewsletterDeleteView.as_view(),
        name="newsletter_delete",
    ),
    path("attempts/", AttemptsListView.as_view(), name="attempts_list"),
    path(
        "newsletter/create/", NewsletterCreateView.as_view(), name="newsletter_create"
    ),
    path(
        "newsletter_send/<int:pk>/",
        SendNewsLetterList.as_view(),
        name="sendnewsletterlist",
    ),
    path(
        "newsletter/<int:pk>/", NewsLetterDetailView.as_view(), name="newsletter_detail"
    ),
]
