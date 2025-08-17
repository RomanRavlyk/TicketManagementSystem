from rest_framework.permissions import BasePermission

from ticket.models import Ticket


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

class IsOwnerPermissionMarks(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.support_user == request.user

class IsAssignedToMarks(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        ticket_id = view.kwargs.get('ticket_id')
        if ticket_id:
            ticket = Ticket.objects.get(id=ticket_id)
            return request.user in ticket.assigned_to.all()
        return True

    def has_object_permission(self, request, view, obj):
        ticket = obj.ticket
        return request.user in ticket.assigned_to.all()