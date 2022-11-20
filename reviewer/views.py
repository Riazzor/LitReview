from django.contrib.auth.views import LoginView, LogoutView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

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


class FluxView(LoginRequiredMixin, ListView):
    """
    The 'Flux'
    This is the list with all tickets and reviews
    including those whom don't belongs to the loged user.
    """
    model = Ticket
    template_name = 'reviewer/list_ticket.html'
    context_object_name = 'flux_elements'

    def get_queryset(self):
        """
        Only one list containing both tickets with review and tickets not reviewed yet.
        The reason they are not in two separate context is because this way is easier
        for sorting by time_created.
        """
        tickets = super().get_queryset()
        # We fetch reviews of already reviewed tickets in the same list to sort by time_created :
        intermediate_queryset = []
        # id of ticket already reviewed by current user :
        reviewed_ticket_id = []
        for ticket in tickets:
            intermediate_queryset.append(ticket)
            if reviews := ticket.reviews.all():
                for review in reviews:
                    if review.user_id == self.request.user.id:
                        reviewed_ticket_id.append(review.ticket_id)
                intermediate_queryset.extend(reviews)
        intermediate_queryset.sort(key=lambda elem: elem.time_created, reverse=True)

        # Creating dict for each element. ==>
        # {
        #   'button': create | '' if not already reviewed by current user,
        #   'review': review or None if is a review,
        #   'ticket': ticket or None if is a ticket,
        # }
        # for each tickets, if not already reviewed by current user, create button :
        queryset = []
        for elem in intermediate_queryset:
            button = 'create'
            if type(elem) == Review:
                if elem.ticket_id in reviewed_ticket_id:
                    button = ''
                flux_elements = {
                    'button': button,
                    'review': elem,
                    'ticket': None,
                }
            else:
                if elem.id in reviewed_ticket_id:
                    button = ''
                flux_elements = {
                    'button': button,
                    'review': None,
                    'ticket': elem,
                }
            queryset.append(flux_elements)

        return queryset


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
        form.instance.ticket_id = self.request.GET.get('ticket_id')
        return super().form_valid(form)


class CurrentUserPostsView(LoginRequiredMixin, ListView):
    """
    This is the list of tickets and reviews created by
    the current user.
    """
    model = Review
    template_name = 'reviewer/list_ticket.html'
    context_object_name = 'flux_elements'

    def get_queryset(self):
        user_id = self.request.user.id
        intermediate_queryset = []
        intermediate_queryset.extend(super().get_queryset().filter(user_id=user_id))
        intermediate_queryset.extend(Ticket.objects.filter(user_id=user_id))
        intermediate_queryset.sort(key=lambda elem: elem.time_created, reverse=True)

        # Creating dict for each element. ==>
        # {
        #   'button': modify,
        #   'review': review or None if is a review,
        #   'ticket': ticket or None if is a ticket,
        # }
        # for each tickets, if not already reviewed by current user, create button :
        queryset = []
        for elem in intermediate_queryset:
            button = 'modify'
            if type(elem) == Review:
                flux_elements = {
                    'button': button,
                    'review': elem,
                    'ticket': None,
                }
            else:
                flux_elements = {
                    'button': button,
                    'review': None,
                    'ticket': elem,
                }
            queryset.append(flux_elements)
        return queryset


ERROR = {
    'subscription_exist': 'Cet abonnement existe déjà !',
    'no_subscription': 'Cet abonnement n\'existe pas',
}


class SearchUserView(LoginRequiredMixin, ListView):
    """
    View gives the list of users followed and the list of is_following users.
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
            user_followed = [
                user.followed_user
                for user in self.request.user.is_following.all()
            ]
            for user in users:
                if user not in user_followed:
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
        if self.request.user.is_following.filter(followed_user_id=self.request.POST.get('id')):
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


class UpdateTicketView(UpdateView):
    template_name = 'reviewer/update_ticket.html'
    model = Ticket
    # fields = ['title', 'description', 'image']
    # http_method_names = ['post']
    success_url = reverse_lazy('reviewer:list_review')
    extra_context = {
        'submit_button': 'Modifier',
    }
    form_class = TicketForm


class UpdateReviewView(UpdateView):
    template_name = 'reviewer/update_review.html'
    model = Review
    # fields = ['rating', 'headline', 'body']
    # http_method_names = 'post']
    success_url = reverse_lazy('reviewer:list_review')
    extra_context = {
        'submit_button': 'Modifier',
    }
    form_class = ReviewForm
