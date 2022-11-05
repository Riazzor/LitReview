from django.contrib.auth.views import LoginView, LogoutView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, ListView, View

from .forms import MyAuthenticationForm, MyUserCreationForm, ReviewForm, TicketForm
from .mixins import AnonymousMixins
from .models import Review, Ticket, UserFollows


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


class CreateTicketView(LoginRequiredMixin, CreateView):
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


class DetailTicketView(LoginRequiredMixin, DetailView):
    model = Ticket
    context_object_name = 'ticket'


class ListTicketView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'reviewer/list_ticket.html'
    context_object_name = 'tickets'


class CreateReviewFromTicketView(LoginRequiredMixin, CreateView):
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


class ListReviewView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'reviewer/list_review.html'
    context_object_name = 'reviews'


ERROR = {
    'subscription_exist': 'Cet abonnement existe déjà !',
    'no_subscription': 'Cet abonnement n\'existe pas',
}


class SearchUserView(LoginRequiredMixin, ListView):
    """
    View gives the list of users followed and the list of following users.
    """
    template_name = 'reviewer/list_followed_user.html'
    model = User
    context_object_name = 'searched_users'
    no_user_found = False

    def get_queryset(self, *args, **kwargs):
        searched_users = []
        pk = self.request.user.pk
        if name := self.request.GET.get('name'):
            users = super().get_queryset(*args, **kwargs).exclude(pk=pk).filter(username__icontains=name)
            user_followed = [user.followed_user for user in UserFollows.objects.filter(user=self.request.user)]
            for user in users:
                if user not in user_followed and user:
                    searched_users.append(user)
            if not searched_users:
                self.no_user_found = True
        return searched_users

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['followed_users'] = UserFollows.objects.filter(user=self.request.user)
        context['following_users'] = UserFollows.objects.filter(followed_user=self.request.user)
        if self.no_user_found:
            context['error'] = "L'utilisateur recherché n'existe pas ou est déjà suivit."
        else:
            context['error'] = ERROR.get(self.request.GET.get('error'), '')

        return context


class SubscribeView(View):
    """
    A subscribe user inside of the user followed page. Supporting only POST method.
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        # check if user not already followed
        if self.request.user.following.filter(followed_user_id=self.request.POST.get('id')):
            return redirect(reverse('reviewer:list_subscriber') + '?error=subscription_exist')
        UserFollows.objects.create(user=self.request.user, followed_user_id=self.request.POST.get('id'))
        return redirect(reverse('reviewer:list_subscriber'))


class UnsubscribeView(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        # check if subscription exist
        error = ''
        if not (subscription := UserFollows.objects.filter(id=self.request.POST.get('id'))):
            error = "?error=no_subscription"
        subscription.delete()
        return redirect(reverse('reviewer:list_subscriber') + error)
