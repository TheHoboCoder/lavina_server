from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register', views.RegisterView.as_view()),
    path('login_web', auth_views.LoginView.as_view()),
    path('login', views.LoginView.as_view()),
    path('logout', views.LogoutView.as_view()),
    path('crsf', views.get_crsf),
    path('whoami', views.WhoamiView.as_view()),
    path('places', views.ListCreatePlacesView.as_view()),
    path('allowed_region', views.get_allowed_region),
    path('places/<pk>', views.UpdatePlacesView.as_view()),
    path('elevation_around/<lat>/<lng>', views.ElevationAPI.as_view()),
    path('exp_elevation/<lat>/<lng>/<fraction>', views.ExperimentalElevationAPI.as_view())
] 