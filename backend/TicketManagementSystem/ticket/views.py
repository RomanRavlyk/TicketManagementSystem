from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Ticket

from .serializers import (TicketCreateSerializer, TicketResponseSerializer, TicketUpdateSerializer,
                          AdminTicketCreateSerializer, AdminTicketUpdateSerializer, AdminTicketResponseSerializer,
                          SupportTicketResponseSerializer,
                          )

from users.permissions import (IsSuperUserPermission, IsSupportPermission)
from rest_framework.response import Response
from .permissions import IsOwnerPermission, IsAssignedTo
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.utils import timezone

from users.models import CustomUser


class UserTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    lookup_field = 'id'
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['id', 'status']
    ordering_fields = ['id', 'status']
    search_fields = ['title']

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return TicketUpdateSerializer

    def get_permissions(self):
        if self.action == 'create' or self.action == 'list':
            return [IsAuthenticated()]
        else:
            return [IsOwnerPermission(), IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = TicketCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=200)

    def retrieve(self, request, *args, **kwargs):
        ticket = self.get_object()
        return Response(TicketResponseSerializer(ticket, context={'request': request}).data, status=200)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(created_by=request.user.id)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = TicketResponseSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        tickets = self.get_queryset().filter(
            created_by=request.user.id)  # add filtering for open/closed tickets, maybe some ordering
        return Response(TicketResponseSerializer(tickets, context={'request': request}, many=True).data, status=200)

    def update(self, request, *args, **kwargs):
        ticket = self.get_object()

        serializer = TicketUpdateSerializer(ticket, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(TicketResponseSerializer(serializer.instance, context={'request': request}).data, status=200)

    def partial_update(self, request, *args, **kwargs):
        ticket = self.get_object()

        serializer = TicketUpdateSerializer(ticket, data=request.data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(TicketResponseSerializer(serializer.instance, context={'request': request}).data, status=200)

    def destroy(self, request, *args, **kwargs):
        ticket = self.get_object()

        ticket.status = Ticket.Status.CLOSED
        ticket.closed_at = timezone.now()
        ticket.save()
        return Response({'message': 'Ticket has been closed'})


class SupportTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    permission_classes = [IsSupportPermission, IsAssignedTo]
    lookup_field = 'id'
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['id', 'status', 'priority']
    ordering_fields = ['id', 'status', 'priority']
    search_fields = ['title']

    def retrieve(self, request, *args, **kwargs):
        ticket = self.get_object()
        return Response(SupportTicketResponseSerializer(ticket, context={'request': request}).data, status=200)

    def list(self, request, *args, **kwargs):
        tickets = self.filter_queryset(self.get_queryset()).filter(assigned_to=request.user.id)
        page=self.paginate_queryset(tickets)
        if page is not None:
            serializer = SupportTicketResponseSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        return Response(TicketResponseSerializer(tickets, context={'request': request}, many=True).data, status=200)

    # def update(self, request, *args, **kwargs):
    #     ticket = self.get_object()

    def destroy(self, request, *args, **kwargs):
        ticket = self.get_object()
        user = CustomUser.objects.get(id=request.user.id)

        ticket.status = Ticket.Status.CLOSED
        ticket.closed_at = timezone.now()
        ticket.completed_by = user

        ticket.save()
        return Response({'message': 'Ticket has been closed'})

class SupportTicketMarksViewSet(viewsets.ModelViewSet):
    pass

#todo: admin stats for most active supports,
# number of created tickets per time period

class AdminTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    # permission_classes = [IsSuperUserPermission]
    serializer_class = AdminTicketResponseSerializer
    lookup_field = 'id'
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['id', 'status', 'priority', 'assigned_to__id', 'created_by__id']
    search_fields = ['title', 'description']
    ordering_fields = ['id', 'status', 'priority', 'created_at']
    ordering = ['id']

    def create(self, request, *args, **kwargs):
        serializer = AdminTicketCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AdminTicketResponseSerializer(serializer.instance, context={'request': request}).data, status=200)

    def list(self, request, *args, **kwargs):
        tickets = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(tickets)
        if page is not None:
            serializer = AdminTicketResponseSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = AdminTicketResponseSerializer(tickets, many=True, context={'request': request})
        return Response(serializer.data, status=200)

    def retrieve(self, request, *args, **kwargs):
        ticket = self.get_object()
        return Response(AdminTicketResponseSerializer(ticket, context={'request': request}).data, status=200)

    def update(self, request, *args, **kwargs):
        ticket = self.get_object()
        serializer = AdminTicketUpdateSerializer(ticket, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(AdminTicketResponseSerializer(serializer.instance, context={'request': request}).data, status=200)

    def partial_update(self, request, *args, **kwargs):
        ticket = self.get_object()
        serializer = AdminTicketUpdateSerializer(ticket, data=request.data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AdminTicketResponseSerializer(serializer.instance, context={'request': request}).data, status=200)

    def destroy(self, request, *args, **kwargs):
        ticket = self.get_object()
        ticket.delete()
        return Response({"message": "Ticket has been deleted"}, status=200)
