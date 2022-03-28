from rest_framework import permissions
from rest_framework.generics import CreateAPIView, UpdateAPIView

from .serializers import UserRegSerializer

class RegisterView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegSerializer

