from rest_framework.serializers import ModelSerializer
from .models import CustomUser

class UserCreateSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email",]

class UserChangeSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email"]

class UserResponseSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role", "date_joined", "is_active"]

class AdminUserCreateSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "role", "is_staff", "is_superuser", "is_active"]

    def create(self, validated_data):
        return CustomUser.objects.create(**validated_data)

class AdminUpdateUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "role", "is_staff", "is_superuser", "is_active"]

class AdminUserResponseSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role", "is_staff", "is_superuser", "date_joined", "is_active", "last_login"]