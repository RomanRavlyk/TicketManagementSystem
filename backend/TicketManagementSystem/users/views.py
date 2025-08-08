from django.core.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import CustomUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsUserPermission, IsSupportPermission, IsSuperUserPermission
from .serializers import (UserCreateSerializer,
                          UserChangeSerializer,
                          UserResponseSerializer,
                          AdminResponseUserSerializer,
                          AdminUpdateUserSerializer, AdminCreateUserSerializer)
from rest_framework.generics import ListCreateAPIView
from django_filters.rest_framework import DjangoFilterBackend

#USER VIEWS#
class UserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return UserChangeSerializer
        elif self.action in ["list", "retrieve"]:
            return UserResponseSerializer
        return super().get_serializer_class()

#todo:
# some statistics for admin panel,
# email send on user creation,
# force password reset

#ADMIN VIEWS#
class AdminUserListORCreateView(ListCreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [IsSuperUserPermission]
    serializer_class = AdminResponseUserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role']
    search_fields = ["username", "email"]
    ordering_fields = ["role"]

    def create(self, request, *args, **kwargs):
        try:
            serializer = (AdminCreateUserSerializer(data=request.data))
            serializer.is_valid(raise_exception=True)
            created_user = serializer.save()
            return Response(AdminResponseUserSerializer(created_user).data)
        except ValidationError as e:
            return Response({"error": e.messages}, status=400)

class AdminUserUpdateAPIView(APIView):
    permission_classes = [IsSuperUserPermission]
    serializer_class = AdminUpdateUserSerializer

    def get(self, request, *args, **kwargs):
        try:
            if kwargs["id"]:
                user = CustomUser.objects.get(id=kwargs['id'])
                return Response(AdminResponseUserSerializer(user).data)
            else:
                raise CustomUser.DoesNotExist("User not fount")
        except Exception as e:
            return Response({"error": e}, status=404)

    def patch(self, request, **kwargs):
        try:
            user = CustomUser.objects.get(id=kwargs.get("id"))
        except CustomUser.DoesNotExist:
            return Response({"Error": "User not exist"}, status=404)

        serializer = AdminUpdateUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(AdminResponseUserSerializer(user).data)
        return Response(serializer.errors, status=400)

    def delete(self, request, **kwargs):
        try:
            user = CustomUser.objects.get(id=kwargs.get("id"))
            user.delete()
            return Response({"Response": "User was successfully deleted"}, status=204)
        except CustomUser.DoesNotExist:
            return Response({"Error": "User not exist"}, status=404)

class AdminGetActiveUsersCountStats(): pass #SHOULD RETURN ACTIVE/INACTIVE USER COUNTS


class AdminUserRegistrationStats(): pass #Should return number of registered users per time part for example 1 month

