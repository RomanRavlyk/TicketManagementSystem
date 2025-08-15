from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import CustomUser
from rest_framework.validators import UniqueValidator

class BaseUserSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(
            queryset=CustomUser.objects.all(),
            message="This username is already in use."
        )], required=False
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=CustomUser.objects.all(),
            message="This email is already in use."
        )], required=False
    )

    def validate_password(self, password):
        validate_password(password)
        return password

    class Meta:
        model = CustomUser
        fields = ["username", "email"]


# USER SERIALIZERS#
class UserCreateSerializer(BaseUserSerializer):
    username = serializers.CharField(validators=[UniqueValidator(
        queryset=CustomUser.objects.all(),
        message="This username is already in use."
    )], required=True)

    email = serializers.EmailField(validators=[UniqueValidator(
        queryset=CustomUser.objects.all(),
        message="This email is already in use."
    )], required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = BaseUserSerializer.Meta.fields + ["password"]

    def create(self, validated_data):
        password = validated_data["password"]
        validate_password(password)
        return CustomUser.objects.create_user(**validated_data)


class UserChangeSerializer(BaseUserSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = BaseUserSerializer.Meta.fields + ["password"]

        extra_kwargs = {
            'url': {'view_name': 'user-detail', 'lookup_field': 'id'}
        }

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)

        if validated_data.get('password'):
            password = validated_data["password"]
            validate_password(password)
            instance.set_password(password)

        instance.save()

        return instance


class UserResponseSerializer(BaseUserSerializer):
    class Meta:
        model = CustomUser
        fields = BaseUserSerializer.Meta.fields + ["id", "url"]

        extra_kwargs = {
            'url': {'view_name': 'user-detail', "lookup_field": "id"}
        }


# ADMIN SERIALIZERS#
class AdminCreateUserSerializer(BaseUserSerializer):
    username = serializers.CharField(validators=[UniqueValidator(
        queryset=CustomUser.objects.all(),
        message="This username is already in use."
    )], required=True)
    email = serializers.EmailField(validators=[UniqueValidator(
        queryset=CustomUser.objects.all(),
        message="This email is already in use."
    )], required=True)
    role = serializers.ChoiceField(choices=["USER", "SUPPORT", "ADMIN"], required=True)

    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = BaseUserSerializer.Meta.fields + ["password", 'role', 'is_active']

    def create(self, validated_data):
        password = validated_data["password"]
        validate_password(password)

        if validated_data["role"] == "ADMIN":
            validated_data["is_staff"] = True
            validated_data["is_superuser"] = True

        if validated_data["role"] == "SUPPORT":
            validated_data["is_staff"] = True

        return CustomUser.objects.create_user(**validated_data)


class AdminUpdateUserSerializer(BaseUserSerializer):
    role = serializers.ChoiceField(choices=["USER", "SUPPORT", "ADMIN"], required=True)

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = BaseUserSerializer.Meta.fields + ["password", 'role', 'is_active']

        extra_kwargs = {
            'url': {'view_name': 'admin_change_user', 'lookup_field': 'id'}
        }

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        if validated_data.get('password'):
            password = validated_data["password"]
            validate_password(password)
            instance.set_password(password)

        role = validated_data.get("role", instance.role)
        instance.role = role
        if role == "ADMIN":
            instance.is_staff = True
            instance.is_superuser = True
        elif role == "SUPPORT":
            instance.is_staff = True
            instance.is_superuser = False
        else:
            instance.is_staff = False
            instance.is_superuser = False

        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.save()

        return instance


class AdminResponseUserSerializer(BaseUserSerializer):
    class Meta:
        model = CustomUser
        fields = BaseUserSerializer.Meta.fields + ["id", "url", "role", "is_staff", "is_superuser", "date_joined",
                                                   "is_active",
                                                   "last_login"]

        extra_kwargs = {
            'url': {'view_name': 'admin_change_user', "lookup_field": "id"}
        }


class AdminUserRegisteredStatsSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField(required=True)
    end_date = serializers.DateTimeField(required=True)
