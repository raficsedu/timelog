from django.contrib.auth.hashers import make_password
from django.utils import timezone
from timetracker.services import format_response, get_tokens_for_user
from users.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.contrib.auth import authenticate


class UserRegister(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        # Copy data to modify
        data = request.data.copy()
        if 'email' in data:
            data['email'] = data['email'].lower()

        # Serializer validation
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            # Save user
            user = serializer.save(password=make_password(data['password']))
            return Response(format_response(UserDataSerializer(user).data, 'Created', 201),
                            status=status.HTTP_201_CREATED)
        else:
            return Response(format_response(serializer.errors, 'Bad Request', 400), status=status.HTTP_400_BAD_REQUEST)


class UserAuthenticate(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        # Serializer validation
        serializer = AuthenticateSerializer(data=request.data)
        if serializer.is_valid():
            # Authenticate user by email or username
            user = authenticate(request, email=request.data.get('email'), password=request.data.get('password'))

            if user:
                # Remove Password from Payload
                user_data = UserDataSerializer(user).data.copy()
                user_data.pop('password', None)

                # Last login
                user.last_login = timezone.now()
                user.save()

                # Adding Token
                user_data['token'] = get_tokens_for_user(user)
                return Response(format_response(user_data, 'Success', 200), status=status.HTTP_200_OK)
            else:
                return Response(
                    format_response({'authentication': ['Email or Password is incorrect']}, 'Not Found', 404),
                    status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(format_response(serializer.errors, 'Bad Request', 400), status=status.HTTP_400_BAD_REQUEST)
