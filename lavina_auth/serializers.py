from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

class UserRegSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password"]
        extra_kwargs = {
            'username':   {'required': True},
            'first_name': {'required': True},
            'last_name':  {'required': True},
            'password':   {'required': True},
        }

    def create(self, validated_data):

        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
        )
        
        user.set_password(validated_data['password'])
        user.save()

        regular_user_group = Group.objects.get(name='regular_user') 
        regular_user_group.user_set.add(user)

        return user