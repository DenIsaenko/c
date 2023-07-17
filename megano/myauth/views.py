import json

from django.contrib.auth import login, authenticate
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from .serializers import ProfileSerializer, AvatarSerializer
from .models import Profile, Avatar


class SignInView(APIView):
    def post(self, request):
        user_data = json.loads(request.body)
        username = user_data.get("username")
        password = user_data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response(
                status=status.HTTP_201_CREATED
            )  # статусы такие берутся от сюда from rest_framework import status

        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class ChangeAvatarView(APIView):
#     parser_classes = [MultiPartParser, FormParser]
#
#     def post(self, request, format=None):
#         serializer = AvatarSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(avatar=request.FILES.get('avatar'))
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)
class ChangeAvatarView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        profile = request.user.profile

        # Получаем файл аватара из запроса
        avatar_file = request.FILES.get("avatar")

        if avatar_file:
            # Создаем или обновляем аватар в профиле пользователя
            avatar, created = Avatar.objects.get_or_create()
            avatar.src = avatar_file
            avatar.alt = "avatar"
            avatar.save()

            # Обновляем поле аватара в профиле пользователя
            profile.avatar = avatar
            profile.save()

            # Сериализуем аватар и возвращаем его в ответе
            serializer = AvatarSerializer(avatar)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"error": "No avatar file provided"}, status=status.HTTP_400_BAD_REQUEST
        )


class SignUpView(APIView):
    def post(self, request):
        user_data = json.loads(request.body)
        name = user_data.get("name")
        username = user_data.get("username")
        password = user_data.get("password")

        try:
            user = User.objects.create_user(username=username, password=password)
            profile = Profile.objects.create(user=user, fullName=name)
            profile.save()
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

            return Response(status=status.HTTP_201_CREATED)
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(APIView):
    def post(self, request):
        current_password = request.data.get("currentPassword")
        new_password = request.data.get("newPassword")

        user = authenticate(username=request.user.username, password=current_password)
        if user is None:
            return Response(
                {"error": "Invalid current password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Изменение пароля
        user.set_password(new_password)
        user.save()

        return Response(status=status.HTTP_200_OK)
