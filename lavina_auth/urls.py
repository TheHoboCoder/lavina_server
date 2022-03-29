from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register', views.RegisterView.as_view()),
    path('login_web', auth_views.LoginView.as_view()),
    path('login_token', views.ObtainAuthToken.as_view())
] 