from django.db.models import Count, Max
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Ticket, SupportTicketMarks
from rest_framework.exceptions import MethodNotAllowed

from .serializers import (TicketCreateSerializer, TicketResponseSerializer, TicketUpdateSerializer,
                          AdminTicketCreateSerializer, AdminTicketUpdateSerializer, AdminTicketResponseSerializer,
                          SupportTicketResponseSerializer, SupportUpdateTicketSerializer, SupportCreateMarksSerializer,
                          SupportResponseMarksSerializer, SupportUpdateMarksSerializer, AdminCreatedTicketsSerializer, )

from rest_framework.decorators import action
from users.permissions import (IsSuperUserPermission, IsSupportPermission)
from rest_framework.response import Response
from .permissions import IsOwnerPermission, IsAssignedTo, IsOwnerPermissionMarks, IsAssignedToMarks
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

        return Response(TicketResponseSerializer(serializer.instance, context={'request': request}).data, status=201)

    def retrieve(self, request, *args, **kwargs):
        ticket = self.get_object()
        return Response(TicketResponseSerializer(ticket, context={'request': request}).data, status=200)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(created_by=request.user.id).order_by('id')
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = TicketResponseSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        return Response(TicketResponseSerializer(queryset, context={'request': request}, many=True).data, status=200)

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
        return Response({'message': 'Ticket has been closed'}, status=200)


class SupportTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    permission_classes = [IsSupportPermission, IsAssignedTo, IsOwnerPermission]
    lookup_field = 'id'
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['id', 'status', 'priority']
    ordering_fields = ['id', 'status', 'priority']
    search_fields = ['title']

    def get_permissions(self):
        if self.action in ['take', 'release']:
            return [IsSupportPermission()]
        else:
            return [IsSupportPermission(), IsAssignedTo()]

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')

    def retrieve(self, request, *args, **kwargs):
        ticket = self.get_object()
        support_marks = SupportTicketMarks.objects.filter(ticket=ticket)
        return Response(SupportTicketResponseSerializer(ticket, context={'request': request}).data, status=200)

    def list(self, request, *args, **kwargs):
        tickets = self.filter_queryset(self.get_queryset()).filter(assigned_to=request.user.id).order_by('id')
        page = self.paginate_queryset(tickets)
        if page is not None:
            serializer = SupportTicketResponseSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        return Response(SupportTicketResponseSerializer(tickets, context={'request': request}, many=True).data,
                        status=200)

    def update(self, request, *args, **kwargs):
        ticket = self.get_object()

        serializer = SupportUpdateTicketSerializer(ticket, data=request.data, context={'request': request})
        serializer.is_valid()
        serializer.save()
        return Response(SupportTicketResponseSerializer(serializer.instance, context={'request': request}).data,
                        status=200)

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')

    def destroy(self, request, *args, **kwargs):
        ticket = self.get_object()
        user = CustomUser.objects.get(id=request.user.id)

        ticket.status = Ticket.Status.CLOSED
        ticket.closed_at = timezone.now()
        ticket.completed_by = user

        ticket.save()
        return Response({'message': 'Ticket has been closed'}, status=200)

    @action(detail=True, methods=['post'], url_path='take')
    def take(self, request, id=None):
        ticket = self.get_object()
        ticket.assigned_to.add(request.user.id)
        return Response({"message": f"successfully assigned to ticket: {ticket.id}"}, status=200)

    @action(detail=True, methods=['post'], url_path='release')
    def release(self, request, id=None):
        ticket = self.get_object()
        ticket.assigned_to.remove(request.user.id)
        return Response({"message": f"successfully unassigned from ticket: {ticket.id}"}, status=200)


class SupportTicketMarksViewSet(viewsets.ModelViewSet):
    queryset = SupportTicketMarks.objects.all()
    lookup_field = 'id'
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['id', 'support_user', 'support_status']
    ordering_fields = ['id', 'support_user', 'support_status']

    def get_serializer_class(self):
        if self.action == 'create':
            return SupportCreateMarksSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return SupportUpdateMarksSerializer
        return SupportResponseMarksSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsSupportPermission()]
        if self.action == 'create':
            return [IsSupportPermission(), IsAssignedToMarks()]
        else:
            return [IsSupportPermission(), IsOwnerPermissionMarks()]

    def create(self, request, *args, **kwargs):
        serializer = SupportCreateMarksSerializer(data=request.data,
                                                  context={'request': request, 'ticket_id': kwargs.get('ticket_id')})
        serializer.is_valid(raise_exception=True)
        mark = serializer.save()

        return Response(SupportResponseMarksSerializer(mark).data, status=201)

    def list(self, request, *args, **kwargs):
        # ticket_id = kwargs['ticket_id']
        tickets = self.filter_queryset(self.get_queryset()).order_by('id')
        page = self.paginate_queryset(tickets)
        if page is not None:
            serializer = SupportResponseMarksSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        return Response(SupportResponseMarksSerializer(tickets, context={'request': request}, many=True).data,
                        status=200)

    def retrieve(self, request, *args, **kwargs):
        mark = self.get_object()
        serializer = SupportResponseMarksSerializer(mark, context={'request': request})
        return Response(serializer.data, status=200)

    def update(self, request, *args, **kwargs):
        mark = self.get_object()
        serializer = SupportUpdateMarksSerializer(mark, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(SupportResponseMarksSerializer(serializer.instance, context={'request': request}).data, )

    def partial_update(self, request, *args, **kwargs):
        mark = self.get_object()
        serializer = SupportUpdateMarksSerializer(mark, data=request.data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(SupportResponseMarksSerializer(serializer.instance, context={'request': request}).data, )

    def destroy(self, request, *args, **kwargs):
        mark = self.get_object()
        mark.delete()
        mark.save()
        return Response({'message': 'Mark has been deleted'})

class AdminTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    permission_classes = [IsSuperUserPermission]
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
        return Response(AdminTicketResponseSerializer(serializer.instance, context={'request': request}).data,
                        status=201)

    def list(self, request, *args, **kwargs):
        tickets = self.filter_queryset(self.get_queryset()).order_by('id')
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

        return Response(AdminTicketResponseSerializer(serializer.instance, context={'request': request}).data,
                        status=200)

    def partial_update(self, request, *args, **kwargs):
        ticket = self.get_object()
        serializer = AdminTicketUpdateSerializer(ticket, data=request.data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AdminTicketResponseSerializer(serializer.instance, context={'request': request}).data,
                        status=200)

    def destroy(self, request, *args, **kwargs):
        ticket = self.get_object()
        ticket.delete()
        return Response({"message": "Ticket has been deleted"}, status=200)

    @action(detail=True, methods=['get', 'post'], url_path='marks')
    def marks(self, request, id=None):
        ticket = self.get_object()
        if request.method == 'GET':
            marks = SupportTicketMarks.objects.filter(ticket=ticket)
            serializer = SupportResponseMarksSerializer(marks, many=True, context={'request': request})
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = SupportCreateMarksSerializer(
                data=request.data,
                context={'request': request, 'ticket_id': ticket.id}
            )
            serializer.is_valid(raise_exception=True)
            mark = serializer.save()
            return Response(SupportResponseMarksSerializer(mark, context={'request': request}).data, status=201)

    @action(detail=True, methods=['get', 'put', 'patch', 'delete'], url_path='marks/(?P<mark_id>[^/.]+)')
    def marks_detail(self, request, id=None, mark_id=None):
        ticket = self.get_object()
        try:
            mark = SupportTicketMarks.objects.get(id=mark_id, ticket=ticket)
        except SupportTicketMarks.DoesNotExist:
            return Response({"error": "Mark not found"}, status=404)

        if request.method == "GET":
            return Response(SupportResponseMarksSerializer(mark, context={'request': request}).data)

        elif request.method in ['PUT', 'PATCH']:
            serializer = SupportUpdateMarksSerializer(
                mark,
                data=request.data,
                partial=(request.method == 'PATCH'),
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(SupportResponseMarksSerializer(serializer.instance, context={'request': request}).data)

        elif request.method == 'DELETE':
            mark.delete()
            return Response({"message": "Mark deleted"}, status=200)

    @action(detail=False, methods=['post'], url_path='created')
    def tickets_created(self, request, id=None, mark_id=None):
        serializer = AdminCreatedTicketsSerializer(data=request.data)
        serializer.is_valid()
        created_first = serializer.validated_data['created_first']
        created_second = serializer.validated_data['created_second']

        count = Ticket.objects.filter(created_at__gt=created_first, created_at__lt=created_second).count()

        return Response({"result": count}, status=200)

    @action(detail=False, methods=['get'], url_path='most_active')
    def most_active_support(self, request, id=None, mark_id=None):
        queryset = Ticket.objects.values('completed_by').filter(completed_by__isnull=False)
        max_count = queryset.annotate(total=Count("id")).aggregate(Max("total"))["total__max"]
        most_active = queryset.annotate(total=Count("id")).filter(total=max_count)

        return Response({"most_active_support": list(most_active)}, status=200)
