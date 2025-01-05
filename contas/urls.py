from django.urls import path
from .views import LoginView
from financas.views import HomeView
from contas.views import RegisterView, LogoutView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('home/', HomeView.as_view(), name='home-page'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('reset-password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password/completed/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
]
