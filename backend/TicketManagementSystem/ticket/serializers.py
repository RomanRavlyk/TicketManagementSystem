from users.models import CustomUser
from rest_framework import serializers
from .models import Ticket
from rest_framework.validators import UniqueValidator
from users.serializers import UserResponseSerializer


class TicketBaseSerializer(serializers.HyperlinkedModelSerializer):
    title = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Ticket.objects.all(),
            )
        ], required=False
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
        instance.save()

        return instance


class TicketResponseSerializer(TicketBaseSerializer):
    created_by = UserResponseSerializer(read_only=True)
    assigned_to = UserResponseSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['id', 'url', 'assigned_to', 'created_by', 'status']

        extra_kwargs = {
            'url': {'view_name': 'ticket-detail', 'lookup_field': 'id'}
        }


class AdminTicketCreateSerializer(serializers.HyperlinkedModelSerializer):
    pass
