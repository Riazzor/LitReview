from django.contrib.auth.views import LoginView, LogoutView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .forms import MyAuthenticationForm, MyUserCreationForm, TicketForm, ReviewForm
from .mixins import AnonymousMixins
from .models import Review, Ticket


class MyLoginView(LoginView):
    template_name = 'reviewer/login.html'
    form_class = MyAuthenticationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('reviewer:home')
    extra_context = {
        'submit_button': 'Connexion',
    }


class MyLogoutView(LogoutView):
    pass


class MyRegisterView(AnonymousMixins, CreateView):
    template_name = 'reviewer/register.html'
    form_class = MyUserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('reviewer:home')
    extra_context = {
        'submit_button': "S'inscrire",
    }

    def form_valid(self, form):
        redirect_page = super().form_valid(form)
        user = form.save()
        if user is not None:
            login(self.request, user)
        return redirect_page


class HomePage(LoginRequiredMixin, TemplateView):
    template_name = 'reviewer/home.html'


class CreateTicketView(CreateView):
    template_name = 'reviewer/create_ticket.html'
    success_url = reverse_lazy('reviewer:list_ticket')
    model = Ticket
    form_class = TicketForm
    extra_context = {
        'submit_button': 'Envoyer',
    }

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class DetailTicketView(DetailView):
    model = Ticket
    context_object_name = 'ticket'


class ListTicketView(ListView):
    model = Ticket
    template_name = 'reviewer/list_ticket.html'


class CreateReviewFromTicketView(CreateView):
    template_name = 'reviewer/create_review.html'
    success_url = reverse_lazy('reviewer:list_review')
    model = Review
    form_class = ReviewForm
    extra_context = {
        'submit_button': 'Envoyer',
    }

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ListReviewView(ListView):
    model = Review
    template_name = 'reviewer/list_review.html'
