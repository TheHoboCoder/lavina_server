from rest_framework import permissions
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from .serializers import UserRegSerializer

class RegisterView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegSerializer

class CustomAuthToken(ObtainAuthToken):
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'group': str(user.groups.first()),
            'first_name': user.first_name,
            'last_name': user.last_name
        })
