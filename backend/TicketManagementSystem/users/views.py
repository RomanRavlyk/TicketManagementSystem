from django.core.exceptions import ValidationError
from django.db.models.aggregates import Count
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import CustomUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from .permissions import (IsUserPermission, IsSupportPermission,
                          IsSuperUserPermission, IsCurrentUserPermission)

from .serializers import (UserCreateSerializer, UserChangeSerializer,
                          UserResponseSerializer, AdminResponseUserSerializer,
                          AdminUpdateUserSerializer, AdminCreateUserSerializer,
                          AdminUserRegisteredStatsSerializer)

from rest_framework.generics import (ListCreateAPIView, ListAPIView,
                                     CreateAPIView, RetrieveAPIView,
                                     UpdateAPIView, DestroyAPIView)

from django_filters.rest_framework import DjangoFilterBackend


# User Views
class UserRegisterView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            serializer = UserCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = CustomUser.objects.create_user(**serializer.validated_data)
            return Response(UserResponseSerializer(user).data, status=201)
        except ValidationError as e:
            return Response({"error": e.message}, status=400)


class UserGetMeView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(UserResponseSerializer(request.user).data, status=200)


class UserUpdateView(APIView):
    permission_classes = [IsCurrentUserPermission]

    def put(self, request, *args, **kwargs):
        try:
            user = CustomUser.objects.get(id=kwargs['id'])
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        self.check_object_permissions(request, user)

        serializer = UserChangeSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response("User successfully updated", status=200)
        else:
            return Response({"message": serializer.errors}, status=400)

class UserDeleteView(APIView):
    permission_classes = [IsCurrentUserPermission]

    def delete(self, request):
        user = request.user
        self.check_object_permissions(request, user)
        user.delete()
        return Response("User successfully deleted", status=200)

# todo:
# email send on user creation,
# force password reset

# ADMIN VIEWS#
class AdminListORCreateUserView(ListCreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [IsSuperUserPermission]
    pagination_class = [] #add pagination
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


class AdminChangeUserAPIView(APIView):
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


class AdminUsersActiveInactiveStatsView(APIView):
    """Return counts of active and inactive users."""
    permission_classes = [IsSuperUserPermission]

    def get(self, request, *args, **kwargs):
        queryset = CustomUser.objects.all()
        count_active = queryset.filter(is_active=True).count()
        count_inactive = queryset.filter(is_active=False).count()
        return Response({"Active": count_active, "Inactive": count_inactive})


class AdminUsersRegisteredStatsView(APIView):
    """Return number of registered users per time period (e.g. per month)."""
    permission_classes = [IsSuperUserPermission]

    def post(self, request, *args, **kwargs):
        serializer = AdminUserRegisteredStatsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print("SERIALIZED DATA:", serializer.validated_data)

        start_date = serializer.validated_data["start_date"]
        end_date = serializer.validated_data["end_date"]

        count = CustomUser.objects.filter(
            date_joined__gte=start_date,
            date_joined__lte=end_date,
        ).count()

        return Response({
            "start_date": start_date,
            "end_date": end_date,
            "count": count
        })


class AdminUsersByRoleStatsView(APIView):
    """Return number of users grouped by role."""
    permission_classes = [IsSuperUserPermission]

    def get(self, request, *args, **kwargs):
        stats = CustomUser.objects.values("role").annotate(count=Count("role"))
        return Response({"users_by_role": stats})
