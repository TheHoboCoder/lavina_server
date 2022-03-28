from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register', views.RegisterView.as_view()),
    path('login', auth_views.LoginView.as_view())
] 