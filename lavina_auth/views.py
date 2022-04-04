from django.http import JsonResponse
from rest_framework import permissions
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
import json
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from .models import Place, PlaceType

from .serializers import UserRegSerializer, PlaceSerializer

def get_crsf(request):
    return JsonResponse({'X-CSRFToken': get_token(request)})

@require_POST
def login_view(request):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    username = data.get('username')
    password = data.get('password')

    if username is None or password is None:
        return JsonResponse({'detail': 'Please provide username and password.'}, status=400)

    user = authenticate(username=username, password=password)

    if user is None:
        return JsonResponse({'detail': 'Invalid credentials.'}, status=400)

    login(request, user)
    return JsonResponse({'detail': 'Successfully logged in.'})

# TODO: change to drf api views
def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'You\'re not logged in.'}, status=400)

    logout(request)
    return JsonResponse({'detail': 'Successfully logged out.'})

def whoami_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})

    return JsonResponse({'username': request.user.username})

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegSerializer

class ListCreatePlacesView(generics.ListCreateAPIView):
    serializer_class = PlaceSerializer

    def get_queryset(self):
        place_type_id = self.request.query_params.get('type_id')
        return Place.objects.filter(place_type=place_type_id)

class UpdatePlacesView(generics.UpdateAPIView):
    serializer_class = PlaceSerializer
