from django.urls import path

from . import views

app_name = 'reviewer'
urlpatterns = [
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('logout/', views.MyLogoutView.as_view(), name='logout'),
    path('register/', views.MyRegisterView.as_view(), name='register'),

    path('', views.HomePage.as_view(), name='home'),
    path('flux/', views.FluxView.as_view(), name='list_ticket'),
    path('ticket-create/', views.CreateTicketView.as_view(), name='create_ticket'),
    path('ticket-update/<int:pk>/', views.UpdateTicketView.as_view(), name='update_ticket'),
    path('review-update/<int:pk>/', views.UpdateReviewView.as_view(), name='update_review'),
    path('post/', views.CurrentUserPostsView.as_view(), name='list_review'),
    path('review-create/<int:pk>/', views.CreateReviewFromTicketView.as_view(), name='create_review'),
    path('subscription/', views.SearchUserView.as_view(), name='list_subscriber'),
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/', views.UnsubscribeView.as_view(), name='unsubscribe'),
]
