from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Ticket
from .serializers import TicketCreateSerializer, TicketResponseSerializer, TicketUpdateSerializer
from users.permissions import (IsSuperUserPermission, IsSupportPermission)
from rest_framework.response import Response
from .permissions import IsOwnerPermission
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

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

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        ticket = self.get_object()
        return Response(TicketResponseSerializer(ticket, context={'request': request}).data)

    def list(self, request, *args, **kwargs):
        tickets = self.get_queryset().filter(created_by=request.user.id) #add filtering for open/closed tickets, maybe some ordering
        return Response(TicketResponseSerializer(tickets, context={'request': request}, many=True).data)

    def update(self, request, *args, **kwargs):
        ticket = self.get_object()

        serializer = TicketUpdateSerializer(ticket, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(TicketResponseSerializer(serializer.instance, context={'request': request}).data)

    def partial_update(self, request, *args, **kwargs):
        ticket = self.get_object()

        serializer = TicketUpdateSerializer(ticket, data=request.data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(TicketResponseSerializer(serializer.instance, context={'request': request}).data)

    def destroy(self, request, *args, **kwargs):
        ticket = self.get_object()

        ticket.status = Ticket.Status.CLOSED
        ticket.save()
        return Response({'message': 'Ticket has been closed'})


class SupportTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    permission_classes = [IsSupportPermission] #maybe create assigned_to permission
    lookup_field = 'id'
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['id', 'status', 'priority']
    ordering_fields = ['id', 'status', 'priority']
    search_fields = ['title']

    def list(self, request, *args, **kwargs):
        tickets = self.get_queryset().filter(assigned_to=request.user.id)
        return Response(TicketResponseSerializer(tickets, context={'request': request}, many=True).data)

class AdminTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    permission_classes = [IsSuperUserPermission]
    lookup_field = 'id'
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['id', 'status', 'priority', 'assigned_to__id']
    ordering_fields = ['id', 'status', 'priority']
    search_fields = ['title']

    def create(self, request, *args, **kwargs):
        pass

    def list(self, request, *args, **kwargs):
        tickets = self.get_queryset()
        return Response(TicketResponseSerializer(tickets, context={'request': request}, many=True).data)
