from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Place, PlaceType
from django.contrib.gis.geos import GEOSGeometry
from lavina_auth.elevation_basic import ALLOWED_REGION

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


class UserSerializer(serializers.ModelSerializer):
    fio = serializers.SerializerMethodField('get_fio')
    group = serializers.SerializerMethodField('get_group')

    def get_fio(self, obj):
        return obj.first_name + ' '+ obj.last_name

    def get_group(self, obj):
        return str(obj.groups.all().first())

    class Meta:
        model = User
        fields = ["id", "username", "fio", "group"]

class PlaceSerializer(serializers.ModelSerializer):
    place_type = serializers.PrimaryKeyRelatedField(queryset=PlaceType.objects.all())
    owner = serializers.PrimaryKeyRelatedField(default=None, read_only=True)

    def validate_geometry(self, value):
        extent = value.extent
        if (extent[0] < ALLOWED_REGION[0] and \
            extent[1] < ALLOWED_REGION[1]) or \
           (extent[2] > ALLOWED_REGION[2] and \
            extent[3] > ALLOWED_REGION[3]):
            raise serializers.ValidationError("extent of geometry should be inside allowed region")
        return value

    class Meta:
        model = Place
        exclude = ['relief_map']
        read_only_fields = ["id", "heighest_point", "heighest_elevation"]
