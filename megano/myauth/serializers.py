from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Profile, Avatar


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("name", "login", "password")

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["name"], email=validated_data["login"]
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


# class ProfileImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = ('avatar', 'alt')


class AvatarSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()

    class Meta:
        model = Avatar
        fields = ["src", "alt"]

    def get_src(self, obj):
        return obj.src.url


class ProfileSerializer(serializers.ModelSerializer):
    avatar = AvatarSerializer()

    class Meta:
        model = Profile
        fields = ["fullName", "email", "phone", "avatar"]
