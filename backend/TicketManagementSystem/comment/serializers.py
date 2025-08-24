from rest_framework import serializers
from users.models import CustomUser
from ticket.models import Ticket
from .models import Comment
from ticket.serializers import CreatedBySerializer

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "title"]

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id']

class CommentCreateSerializer(serializers.ModelSerializer):
    parent = serializers.IntegerField(required=False)
    comment_text = serializers.CharField(required=False, max_length=500)

    class Meta:
        model = Comment
        fields = ['parent', 'comment_text']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        ticket_id = self.context['ticket_id']

        if 'parent' in validated_data:
            parent_id = validated_data.pop('parent')
            validated_data['parent'] = Comment.objects.get(id=parent_id)

        validated_data['ticket'] = Ticket.objects.get(id=ticket_id)
        return Comment.objects.create(**validated_data)

class CommentUpdateSerializer(serializers.ModelSerializer):
    comment_text = serializers.CharField(required=False, max_length=500)

    class Meta:
        model = Comment
        fields = ['comment_text']

class CommentResponseSerializer(serializers.ModelSerializer):
    parent = CommentSerializer(read_only=True)
    created_by = CreatedBySerializer(read_only=True)
    ticket = TicketSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'created_by', 'ticket', 'parent', 'comment_text', 'created_on']


class AdminCreateCommentSerializer(serializers.ModelSerializer):
    created_by = serializers.IntegerField(required=True)
    parent = serializers.IntegerField(required=False)
    comment_text = serializers.CharField(required=False, max_length=500)

    class Meta:
        model = Comment
        fields = ['created_by', 'parent', 'comment_text']

    def create(self, validated_data):
        ticket_id = self.context['ticket_id']
        validated_data['ticket'] = Ticket.objects.get(id=ticket_id)

        validated_data['created_by'] = CustomUser.objects.get(id=validated_data['created_by'])

        if 'parent' in validated_data:
            parent_id = validated_data.pop('parent')
            validated_data['parent'] = Comment.objects.get(id=parent_id)

        return Comment.objects.create(**validated_data)

class AdminUpdateCommentSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False)
    comment_text = serializers.CharField(required=False, max_length=500)

    class Meta:
        model = Comment
        fields = ['parent', 'comment_text']

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class AdminResponseCommentSerializer(serializers.ModelSerializer):
    parent = CommentSerializer(read_only=True)
    created_by = CreatedBySerializer(read_only=True)
    ticket = TicketSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'created_by', 'ticket', 'parent', 'comment_text', 'created_on']

