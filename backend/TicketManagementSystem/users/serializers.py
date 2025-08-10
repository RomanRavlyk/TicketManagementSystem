from rest_framework import serializers
from .models import CustomUser
from rest_framework.validators import UniqueValidator


# USER SERIALIZERS#
class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "password"]


class UserChangeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=CustomUser.objects.all(),
                message="This username is already in use."
                )
        ], required=False
    )

    email = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=CustomUser.objects.all(),
                message="This email is already in use."
                )
        ], required=False
    )

    # todo create validator for user password
    # password = serializers.CharField(validators=[], required=False)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password"]



class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role", "date_joined", "is_active"]


# ADMIN SERIALIZERS#
class AdminCreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "password", "email", "role", "is_staff", "is_superuser", "is_active"]

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class AdminUpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "role", "is_staff", "is_superuser", "is_active"]


class AdminResponseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role", "is_staff", "is_superuser", "date_joined", "is_active",
                  "last_login"]


class AdminUserRegisteredStatsSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField(required=True)
    end_date = serializers.DateTimeField(required=True)
