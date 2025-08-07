from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

class RolePermission(BasePermission):
    roles = []
    def has_permission(self, request, view):

        if request.user.is_anonymous:
            raise PermissionDenied

        return (request.user and request.user.role in self.roles)

class IsSuperUserPermission(RolePermission):
    roles = ["ADMIN"]

class IsSupportPermission(RolePermission):
    roles = ["SUPPORT"]

class IsUserPermission(RolePermission):
    roles = ["USER"]