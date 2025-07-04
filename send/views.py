from datetime import timezone, timedelta
from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import (
    TemplateView,
    CreateView,
    DeleteView,
    ListView,
    DetailView,
    UpdateView,
)

from send.forms import (
    ClientForm,
    ClientManagerForm,
    MessageForm,
    MessageManagerForm,
    NewsletterForm,
    NewsletterManagerForm,
)
from send.models import Newsletter, Client, Message, MailAttempt
from users.email_func.sendingemail import send_email


class HomePageView(TemplateView):
    template_name = "send/home.html"
    success_url = reverse_lazy("send:home")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "newsletter_all": Newsletter.objects.count(),
                "newsletter": Newsletter.objects.filter(
                    status_news_letter="LAUNCHED"
                ).count(),
                "mailings": Client.objects.count(),
            }
        )
        return ctx


class ClientView(LoginRequiredMixin, ListView):
    model = Client
    form_class = ClientForm
    template_name = "send/client_list.html"
    success_url = reverse_lazy("send:home")

    def get_all_clients(get_all_clients=None):
        # Получение списка получателей из базы данных
        clients = Client.objects.all()
        return clients


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("send:home")

    def form_valid(self, form):
        client = form.save()
        user = self.request.user
        client.owner = user
        client.save()
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "send/client_update.html"
    success_url = reverse_lazy("send:home")

    def form_valid(self, form):
        client = form.save()
        user = self.request.user
        client.owner = user
        client.save()
        return super().form_valid(form)

    def get_form_class(self):
        user = self.request.user
        if user == self.object.owner:
            return ClientForm
        if (
            user.has_perm("can_edit_email")
            and user.has_perm("can_edit_name")
            and user.has_perm("can_edit_comment")
        ):
            return ClientManagerForm
        raise PermissionDenied


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = LoginRequiredMixin
    template_name = "send/client_delete.html"
    success_url = reverse_lazy("users:home")


class MessageListView(ListView):
    model = Message
    template_name = "send/message_list.html"
    success_url = reverse_lazy("send:home")

    def get_queryset(self):
        return Message.objects.all()

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.request.user == self.object.owner:
            self.object.views_counter += 1
            self.object.save()
            return self.object
        raise PermissionDenied


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("send:home")

    def form_valid(self, form):
        message = form.save()
        user = self.request.user
        message.owner = user
        message.save()
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "send/message_update.html"
    success_url = reverse_lazy("send:home")

    def form_valid(self, form):
        message = form.save()
        user = self.request.user
        message.owner = user
        message.save()
        return super().form_valid(form)

    def get_form_class(self):
        user = self.request.user
        if user == self.object.owner:
            return MessageForm
        if user.has_perm("send.can_edit_subject_letter") and user.has_perm(
            "send.can_edit_letter"
        ):
            return MessageManagerForm
        raise PermissionDenied


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "send/message_delete.html"
    success_url = reverse_lazy("send:home")


class NewsletterListView(LoginRequiredMixin, ListView):
    model = Newsletter
    template_name = "send/newsletter_list.html"
    success_url = reverse_lazy("send:home")


class NewsLetterDetailView(LoginRequiredMixin, DetailView):
    model = Newsletter
    template_name = "send/newsletter_detail.html"
    success_url = reverse_lazy("send:home")


class NewsletterCreateView(LoginRequiredMixin, CreateView):
    model = Newsletter
    form_class = NewsletterForm
    success_url = reverse_lazy("send:home")

    def form_valid(self, form):
        message = form.save()
        user = self.request.user
        message.owner = user
        message.save()
        return super().form_valid(form)


class NewsletterUpdateView(LoginRequiredMixin, UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    success_url = reverse_lazy("send:home")

    def form_valid(self, form):
        newsletter = form.save()
        user = self.request.user
        newsletter.owner = user
        newsletter.save()
        return super().form_valid(form)

    def get_form_class(self):
        user = self.request.user
        if user == self.object.owner:
            return NewsletterForm
        if user.has_perm("send.can_edit_disabling_mailings"):
            return NewsletterManagerForm
        raise PermissionDenied


class NewsletterDeleteView(LoginRequiredMixin, DeleteView):
    model = Newsletter
    template_name = "send/newsletter_delete.html"
    success_url = reverse_lazy("send:home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        newsletter = self.get_object()
        context["client"] = " , ".join(
            [client.name for client in newsletter.client.all()]
        )
        return context


class SendNewsLetterList(LoginRequiredMixin, View):
    model = Newsletter
    template_name = "send/newsletter_detail.html"

    @require_POST
    def newsletter_run(request, pk):
        newsletter = get_object_or_404(Newsletter, pk=pk)

        if newsletter.status_news_letter != "COMPLETED":
            client_email = [client.email for client in newsletter.client]
            send_email(
                subject=messages.subject_letter,
                message=messages.letter,
                recipient_list=client_email,
                newsletter=newsletter,
            )

            messages.success(request, "Рассылка запущена")
        else:
            messages.warning(request, "Рассылка уже запущена")
        return redirect("send:newsletter_list")


class AttemptsListView(LoginRequiredMixin, ListView):
    model = MailAttempt
    template_name = "send/attempts_list.html"
    context_object_name = "attempts"
    success_url = reverse_lazy("send:home")
