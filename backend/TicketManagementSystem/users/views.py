from django.core.exceptions import ValidationError
from django.db.models.aggregates import Count
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import CustomUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from .permissions import (IsSuperUserPermission, IsCurrentUserPermission)
from .serializers import (UserCreateSerializer, UserChangeSerializer,
                          UserResponseSerializer, AdminResponseUserSerializer,
                          AdminUpdateUserSerializer, AdminCreateUserSerializer,
                          AdminUserRegisteredStatsSerializer)

from rest_framework.generics import (ListCreateAPIView)

from django_filters.rest_framework import DjangoFilterBackend


# User Views
class UserViewSet(ViewSet):
    queryset = CustomUser.objects.all()
    lookup_field = 'id'

    def get_permissions(self):
        if self.action == 'create':
            return []
        else:
            return [IsCurrentUserPermission()]

    def retrieve(self, request, *args, **kwargs):
        try:
            user = CustomUser.objects.get(id=kwargs['id'])
            self.check_object_permissions(request, user)
            return Response(UserResponseSerializer(user, context={'request': request}).data, status=200)
        except CustomUser.DoesNotExist:
            return Response({"Error": "User not found"}, status=404)

    def create(self, request, *args, **kwargs):
        try:
            serializer = UserCreateSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            created_user = CustomUser.objects.get(email=serializer.validated_data['email'])

            return Response(UserResponseSerializer(created_user, context={'request': request}).data, status=201)

        except ValidationError as e:
            return Response({"error": e.message}, status=400)

    def update(self, request, *args, **kwargs):
        try:
            user = CustomUser.objects.get(id=kwargs['id'])
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        self.check_object_permissions(request, user)

        serializer = UserChangeSerializer(user, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(UserResponseSerializer(user, context={'request': request}).data, status=200)

    def destroy(self, request, *args, **kwargs):
        try:
            user = CustomUser.objects.get(id=kwargs['id'])
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        self.check_object_permissions(request, user)
        user.delete()
        return Response("User successfully deleted", status=200)


# todo:
# email send on user creation,
#maybe create that admin can create a list of users

# ADMIN VIEWS#
class AdminListORCreateUserView(ListCreateAPIView):
    queryset = CustomUser.objects.all().order_by('id')
    # permission_classes = [IsSuperUserPermission]
    serializer_class = AdminResponseUserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role']
    search_fields = ["username", "email"]
    ordering_fields = ["id", "role"]

    def create(self, request, *args, **kwargs):
        try:
            serializer = (AdminCreateUserSerializer(data=request.data, context={'request': request}))
            serializer.is_valid(raise_exception=True)
            created_user = serializer.save()
            return Response(AdminResponseUserSerializer(created_user, context={'request': request}).data)
        except ValidationError as e:
            return Response({"error": e.messages}, status=400)

class AdminChangeUserAPIView(APIView):
    permission_classes = [IsSuperUserPermission]
    serializer_class = AdminUpdateUserSerializer

    def get(self, request, *args, **kwargs):
        try:
            user = CustomUser.objects.get(id=kwargs['id'])
            return Response(AdminResponseUserSerializer(user, context={'request': request}).data)
        except Exception as e:
            return Response({"error": str(e)}, status=404)

    def patch(self, request, **kwargs):
        try:
            user = CustomUser.objects.get(id=kwargs.get("id"))
        except CustomUser.DoesNotExist:
            return Response({"Error": "User not exist"}, status=404)

        serializer = AdminUpdateUserSerializer(user, data=request.data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(AdminResponseUserSerializer(user, context={'request': request}).data)

    def delete(self, request, **kwargs):
        try:
            user = CustomUser.objects.get(id=kwargs.get("id"))
            user.delete()
            return Response({"Response": "User was successfully deleted"}, status=200)
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
