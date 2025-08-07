from django.core.exceptions import ValidationError

from .models import CustomUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsUserPermission, IsSupportPermission, IsSuperUserPermission
from .serializers import (UserCreateSerializer,
                          UserChangeSerializer,
                          UserResponseSerializer,
                          AdminUserResponseSerializer,
                          AdminUpdateUserSerializer, AdminUserCreateSerializer)


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

class AdminUserCreateAPIView(APIView):
    permission_classes = [IsSuperUserPermission]
    serializer_class = AdminUpdateUserSerializer

    def post(self, request):
        try:
            serializer = (AdminUserCreateSerializer(data=request.data))
            serializer.is_valid(raise_exception=True)
            created_user = serializer.save()
            return Response(AdminUserResponseSerializer(created_user).data)
        except ValidationError as e:
            return Response({"error": e.messages}, status=400)

class AdminUserUpdateAPIView(APIView):
    permission_classes = [IsSuperUserPermission]
    serializer_class = AdminUpdateUserSerializer

    def get(self, request, *args, **kwargs):
        try:
            user = CustomUser.objects.get(id=kwargs['id'])
            return Response(AdminUserResponseSerializer(user).data)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

    def patch(self, request, **kwargs):
        try:
            user = CustomUser.objects.get(id=kwargs.get("id"))
        except CustomUser.DoesNotExist:
            return Response({"Error": "User not exist"}, status=404)

        serializer = AdminUpdateUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(AdminUserResponseSerializer(user).data)
        return Response(serializer.errors, status=400)

    def delete(self, request, **kwargs):
        try:
            user = CustomUser.objects.get(id=kwargs.get("id"))
            user.delete()
            return Response({"Response": "User was successfully deleted"}, status=204)
        except CustomUser.DoesNotExist:
            return Response({"Error": "User not exist"}, status=404)