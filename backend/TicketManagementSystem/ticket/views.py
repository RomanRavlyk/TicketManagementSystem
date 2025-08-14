from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Ticket
from .serializers import TicketCreateSerializer, TicketResponseSerializer, TicketUpdateSerializer
from users.permissions import (IsSuperUserPermission, IsSupportPermission, IsOwnerPermission)
from rest_framework.response import Response



class UserTicketViewSet(viewsets.ModelViewSet):

    queryset = Ticket.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return TicketUpdateSerializer

    def get_permission(self):
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
        pass

    def list(self, request, *args, **kwargs):
        tickets = self.get_queryset() #MAKE FILTERING FOR USER CREATED TICKETS
        return Response(TicketResponseSerializer(tickets, context={'request': request}, many=True).data)

    def update(self, request, *args, **kwargs):
        pass

    def partial_update(self, request, *args, **kwargs):
        pass

    def destroy(self, request, *args, **kwargs):
        pass

class SupportTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketCreateSerializer
    permission_classes = [IsSupportPermission]
    lookup_field = 'id'

class AdminTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketCreateSerializer
    permission_classes = [IsSuperUserPermission]
    lookup_field = 'id'

