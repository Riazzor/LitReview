from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


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
