from users.models import CustomUser
from rest_framework import serializers
from .models import Ticket, SupportTicketMarks
from rest_framework.validators import UniqueValidator
from users.serializers import UserResponseSerializer
from django.utils import timezone


class TicketBaseSerializer(serializers.HyperlinkedModelSerializer):
    title = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Ticket.objects.all(),
            )
        ], required=False
    )

    description = serializers.CharField(
        required=False,
        max_length=250
    )

    class Meta:
        model = Ticket
        fields = ['title', 'description']


class TicketCreateSerializer(TicketBaseSerializer):
    title = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Ticket.objects.all(),
            )
        ], required=True
    )

    description = serializers.CharField(
        required=True,
        max_length=250
    )

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        validated_data['status'] = Ticket.Status.OPEN
        validated_data['priority'] = Ticket.Priority.MEDIUM

        return Ticket.objects.create(**validated_data)


class TicketUpdateSerializer(TicketBaseSerializer):
    class Meta:
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['id', 'url']

        extra_kwargs = {
            'url': {'view_name': 'ticket-detail', 'lookup_field': 'id'}
        }

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.updated_at = timezone.now()
        instance.save()

        return instance


class TicketResponseSerializer(TicketBaseSerializer):
    created_by = UserResponseSerializer(read_only=True)
    assigned_to = UserResponseSerializer(read_only=True, many=True)

    class Meta:
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['id', 'url', 'assigned_to', 'created_by', 'status']

        extra_kwargs = {
            'url': {'view_name': 'ticket-detail', 'lookup_field': 'id'}
        }


class SupportCreateMarksSerializer(serializers.ModelSerializer):
    support_status = serializers.CharField(max_length=30, required=False)

    class Meta:
        model = SupportTicketMarks
        fields = ['support_status', 'comment']

    def create(self, validated_data):
        print("Context: ", self.context)

        ticket_id = self.context['ticket_id']
        validated_data['ticket'] = Ticket.objects.get(id=ticket_id)
        validated_data['support_user'] = self.context['request'].user

        if not validated_data.get('support_status'):
            validated_data['support_status'] = SupportTicketMarks.SUPPORT_STATUS.IN_PROGRESS

        return SupportTicketMarks.objects.create(**validated_data)

class SupportUpdateMarksSerializer(serializers.ModelSerializer):
    support_status = serializers.CharField(max_length=30, required=False)

    class Meta:
        model = SupportTicketMarks
        fields = ["support_status", "comment"]


    def update(self, instance, validated_data):
        instance.support_status = validated_data.get('support_status', instance.support_status)
        instance.comment = validated_data.get('comment', instance.comment)

        instance.save()

        return instance

class SupportResponseMarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicketMarks
        fields = "__all__"


class SupportUpdateTicketSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ticket
        fields = ['status']

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)

        instance.save()
        return instance


class SupportTicketResponseSerializer(TicketBaseSerializer):
    created_by = UserResponseSerializer(read_only=True)
    completed_by = UserResponseSerializer(read_only=True)
    support_marks = SupportResponseMarksSerializer(source='ticket_mark', read_only=True, many=True)

    class Meta:
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['id', 'url', 'created_by', "completed_by", 'status',
                                                     'priority', 'created_at', 'updated_at', 'closed_at',
                                                     'support_marks']

        extra_kwargs = {
            'url': {'view_name': 'ticket_support-detail', 'lookup_field': 'id'}
        }


class AdminTicketCreateSerializer(TicketBaseSerializer):
    title = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Ticket.objects.all(),
            )
        ], required=True
    )

    description = serializers.CharField(
        required=True,
        max_length=250
    )

    created_by = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        required=True
    )

    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all().filter(role='SUPPORT'),
        many=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['assigned_to', 'created_by', 'status', 'priority']

    def create(self, validated_data):
        if not validated_data.get('status'):
            validated_data['status'] = Ticket.Status.OPEN

        if not validated_data.get('priority'):
            validated_data['priority'] = Ticket.Priority.MEDIUM

        return Ticket.objects.create(**validated_data)


class AdminTicketUpdateSerializer(TicketBaseSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all().filter(role='SUPPORT'),
        many=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['assigned_to', 'status', 'priority']

        extra_kwargs = {
            'url': {'view_name': 'ticket_admin-detail', 'lookup_field': 'id'}
        }

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        instance.priority = validated_data.get('priority', instance.priority)

        instance.updated_at = timezone.now()

        assigned_to = validated_data.get('assigned_to')
        if assigned_to is not None:
            instance.assigned_to.set(assigned_to)

        instance.save()

        return instance


class AdminTicketResponseSerializer(TicketBaseSerializer):
    created_by = UserResponseSerializer(read_only=True)
    assigned_to = UserResponseSerializer(read_only=True, many=True)
    completed_by = UserResponseSerializer(read_only=True)
    support_marks = SupportResponseMarksSerializer(source='ticket_mark', read_only=True, many=True)

    class Meta:
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['id', 'url', 'created_by', 'assigned_to', "completed_by", 'status',
                                                     'priority', 'created_at', 'updated_at', 'closed_at', 'support_marks']

        extra_kwargs = {
            'url': {'view_name': 'ticket_admin-detail', "lookup_field": "id"}
        }
