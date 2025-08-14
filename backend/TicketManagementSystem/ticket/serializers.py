from users.models import CustomUser
from rest_framework import serializers
from .models import Ticket
from rest_framework.validators import UniqueValidator
from users.serializers import UserResponseSerializer


class TicketCreateSerializer(serializers.HyperlinkedModelSerializer):
    title = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Ticket.objects.all(),
            )
        ]
    )

    class Meta:
        model = Ticket
        fields = ['title', 'description']


    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        validated_data['status'] = Ticket.Status.OPEN
        validated_data['priority'] = Ticket.Priority.MEDIUM

        return Ticket.objects.create(**validated_data)

class TicketUpdateSerializer(serializers.HyperlinkedModelSerializer):
    title = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Ticket.objects.all(),
            )
        ]
    )

    # created_by = UserResponseSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'url', 'title', 'description']

        extra_kwargs = {
            'url': {'view_name': 'ticket-detail', 'lookup_field': 'id'}
        }
    pass

class TicketResponseSerializer(serializers.HyperlinkedModelSerializer):
    created_by = UserResponseSerializer(read_only=True)
    assigned_to = UserResponseSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'url', 'title', 'description', 'assigned_to', 'created_by', 'status']
        created_by = UserResponseSerializer(read_only=True)

        extra_kwargs = {
            'url': {'view_name': 'ticket-detail', 'lookup_field': 'id'}
        }