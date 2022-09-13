from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=100, required=True, validators=[
        UniqueValidator(queryset=User.objects.all(), message='Email already exists.')])
    username = serializers.CharField(max_length=25, required=True, validators=[
        UniqueValidator(queryset=User.objects.all(), message='Username already exists.')])
    password = serializers.CharField(min_length=8, max_length=16, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'last_login']


class AuthenticateSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(max_length=16, required=True)

    class Meta:
        model = User
        fields = ['email', 'password']
