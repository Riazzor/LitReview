from django.contrib.auth.views import LoginView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import MyAuthenticationForm, MyUserCreationForm
from .mixins import AnonymousMixins


class MyLoginView(LoginView):
    template_name = 'Reviewer/login.html'
    form_class = MyAuthenticationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('reviewer:home')


class MyRegisterView(AnonymousMixins, CreateView):
    template_name = 'Reviewer/register.html'
    form_class = MyUserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('reviewer:home')

    def form_valid(self, form):
        redirect_page = super().form_valid(form)
        user = form.save()
        if user is not None:
            login(self.request, user)
        return redirect_page


class HomePage(LoginRequiredMixin, TemplateView):
    template_name = 'Reviewer/home.html'
