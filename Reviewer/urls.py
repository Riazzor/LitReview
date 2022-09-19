from django.urls import path

from .views import HomePage, MyLoginView, MyRegisterView

app_name = 'reviewer'
urlpatterns = [
    # path('', views.index, name='index'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('register/', MyRegisterView.as_view(), name='register'),

    path('', HomePage.as_view(), name='home'),
]
