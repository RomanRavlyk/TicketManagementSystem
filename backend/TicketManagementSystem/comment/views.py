from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from .models import Comment
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsCommentOwner
from rest_framework.decorators import action


from .serializers import (CommentResponseSerializer, CommentCreateSerializer, CommentUpdateSerializer,
                          AdminUpdateCommentSerializer, AdminResponseCommentSerializer, AdminCreateCommentSerializer)

from ticket.models import Ticket

from users.permissions import IsSuperUserPermission

class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentResponseSerializer
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        if self.action in ['update', 'partial_update']:
            return CommentUpdateSerializer
        return CommentResponseSerializer

    def get_permissions(self):
        if self.action in ['create', 'retrieve', 'list']:
            return [IsAuthenticated()]
        else:
            return [IsCommentOwner()]

    def get_queryset(self):
        return Comment.objects.filter(ticket__id=self.kwargs['ticket_id'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['ticket_id'] = self.kwargs['ticket_id']
        return context

    def create(self, request, *args, **kwargs):
        if request.data.get('parent'):
            parent = get_object_or_404(Comment, id=request.data['parent'])
            if parent.ticket.id != int(self.kwargs['ticket_id']):
                return Response(
                    {"error": "Parent comment must belong to the same ticket"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = CommentCreateSerializer(data=request.data,
                                             context={'request': request, 'ticket_id': self.kwargs['ticket_id']})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CommentResponseSerializer(serializer.instance, context={'request': request}).data)

    def list(self, request, *args, **kwargs):
        ticket = Ticket.objects.get(id=self.kwargs['ticket_id'])

        queryset = ticket.comments.all()
        serializer = CommentResponseSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        serializer = CommentUpdateSerializer(comment, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CommentResponseSerializer(serializer.instance, context={'request': request}).data)

    def partial_update(self, request, *args, **kwargs):
        comment = self.get_object()
        serializer = CommentUpdateSerializer(comment, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CommentResponseSerializer(serializer.instance, context={'request': request}).data)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        comment.save()
        return Response({"message": "Comment deleted"})

    @action(detail=True, methods=['get'], url_path='replies')
    def get_replies(self, request, ticket_id=None, id=None):
        comment = self.get_object()
        queryset = comment.children.all()
        serializer = CommentResponseSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminCommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperUserPermission]

    def get_serializer_class(self):
        if self.action == 'create':
            return AdminCreateCommentSerializer
        if self.action in ['update', 'partial_update']:
            return AdminUpdateCommentSerializer
        return AdminResponseCommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(ticket_id=self.kwargs['ticket_id'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['ticket_id'] = self.kwargs['ticket_id']
        return context

    def create(self, request, *args, **kwargs):
        if request.data.get('parent'):
            parent = get_object_or_404(Comment, id=request.data['parent'])
            if parent.ticket.id != int(self.kwargs['ticket_id']):
                return Response(
                    {"error": "Parent comment must belong to the same ticket"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = AdminCreateCommentSerializer(data=request.data,
                                             context={'request': request, 'ticket_id': self.kwargs['ticket_id']})

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AdminResponseCommentSerializer(serializer.instance, context={'request': request}).data)

    @action(detail=True, methods=['get'], url_path='replies')
    def get_replies(self, request, ticket_id=None, pk=None):
        comment = self.get_object()
        queryset = comment.children.all()
        serializer = AdminResponseCommentSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
