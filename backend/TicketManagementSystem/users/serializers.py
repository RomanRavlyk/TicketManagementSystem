from rest_framework.serializers import ModelSerializer
from .models import CustomUser

#USER SERIALIZERS#
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

#ADMIN SERIALIZERS#
class AdminCreateUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "password", "email", "role", "is_staff", "is_superuser", "is_active"]

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

class AdminUpdateUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "role", "is_staff", "is_superuser", "is_active"]

class AdminResponseUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role", "is_staff", "is_superuser", "date_joined", "is_active", "last_login"]