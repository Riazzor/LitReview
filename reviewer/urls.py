from django.urls import path

from . import views

app_name = 'reviewer'
urlpatterns = [
    # path('', views.index, name='index'),
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('logout/', views.MyLogoutView.as_view(), name='logout'),
    path('register/', views.MyRegisterView.as_view(), name='register'),

    path('', views.HomePage.as_view(), name='home'),
    path('ticket/', views.ListTicketView.as_view(), name='list_ticket'),
    path('ticket-create/', views.CreateTicketView.as_view(), name='create_ticket'),
    path('review/', views.ListReviewView.as_view(), name='list_review'),
    path('review-create/', views.CreateReviewFromTicketView.as_view(), name='create_review'),
]
