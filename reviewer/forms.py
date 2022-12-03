from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.forms.widgets import Textarea
from django import forms

from .models import Ticket, Review


class MyAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = ''
        self.fields['username'].widget.attrs.update(
            {
                'placeholder': "Nom d'utilisateur",
            }
        )

        self.fields['password'].label = ''
        self.fields['password'].widget.attrs.update(
            {
                'placeholder': 'Mot de passe',
            }
        )


class MyUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = ''
        self.fields['username'].widget.attrs.update(
            {
                'placeholder': "Nom d'utilisateur",
            }
        )

        self.fields['password1'].label = ''
        self.fields['password1'].widget.attrs.update(
            {
                'placeholder': 'Mot de passe',
            }
        )

        self.fields['password2'].label = ''
        self.fields['password2'].widget.attrs.update(
            {
                'placeholder': 'Confirmez mot de passe',
            }
        )


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']
        exclude = ['time_created', ]


class ReviewFromTicketForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'headline', 'body']
        exclude = ['time_created', ]


class ReviewWithoutTicketForm(forms.Form):
    # Ticket fields
    title = forms.CharField(max_length=128)
    description = forms.CharField(max_length=2048, widget=Textarea, required=False)
    image = forms.ImageField(required=False)

    # Review fields
    rating = forms.IntegerField()
    headline = forms.CharField(max_length=128)
    body = forms.CharField(max_length=8192, widget=Textarea, required=False)

    def clean_rating(self):
        rating = self.cleaned_data['rating']
        if not (0 <= rating <= 5) and (rating % 2 != 0):
            raise ValidationError("La note doit être un entier positif entre 0 et 5")
        return rating
