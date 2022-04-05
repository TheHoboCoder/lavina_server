from django.http import JsonResponse
from rest_framework import permissions
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
import json
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, logout
from .models import Place, PlaceType

from .serializers import UserRegSerializer, PlaceSerializer, UserSerializer

def get_crsf(request):
    return JsonResponse({'X-CSRFToken': get_token(request)})

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')
        if username is None or password is None:
            return Response({'detail': 'Please provide username and password.'}, status=400)

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials.'}, status=400)

        login(request, user)
        return Response({'detail': 'Successfully logged in.'})


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        logout(request)
        return Response({'detail': 'Successfully logged out.'})

class WhoamiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        return Response(UserSerializer(request.user).data)

   
class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegSerializer

class ListCreatePlacesView(generics.ListCreateAPIView):
    serializer_class = PlaceSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        place_type_id = self.request.query_params.get('type_id')
        return Place.objects.filter(place_type=place_type_id)
    
    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

class UpdatePlacesView(generics.UpdateAPIView):
    serializer_class = PlaceSerializer
