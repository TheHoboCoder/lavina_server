from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register', views.RegisterView.as_view()),
    path('login_web', auth_views.LoginView.as_view()),
    path('login', views.login_view),
    path('logout', views.logout_view),
    path('crsf', views.get_crsf),
    path('whoami', views.whoami_view),
    path('places', views.ListCreatePlacesView.as_view()),
    path('places/<pk>', views.UpdatePlacesView.as_view()),
] 