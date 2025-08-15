from rest_framework.permissions import BasePermission


class IsOwnerPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user

class IsAssignedTo(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user in obj.assigned_to.filter(id=request.user.id).all()