from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Convversation, Message
from items.models import Item

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    offer_item_name = serializers.CharField(source='offer_item.name', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'conversation',
            'sender',
            'sender_username',
            'content',
            'is_offer',
            'offer_price',
            'offer_item',
            'offer_item_name',
            'offer_status',
            'is_read',
            'timestamp',
        ]
        read_only_fields = [
            'id',
            'sender',
            'sender_username',
            'offer_status',
            'is_read',
            'timestamp',
        ]

    def update(self, instance, validated_data):
        if 'conversation' in validated_data and validated_data['conversation'] != instance.conversation:
            raise ValidationError({'conversation': 'Changing the conversation is not allowed.'})
        return super().update(instance, validated_data)


class MessageCreateSerializer(MessageSerializer):
    conversation = serializers.PrimaryKeyRelatedField(queryset=Convversation.objects.all())

    class Meta(MessageSerializer.Meta):
        pass

    def validate_conversation(self, value):
        user = self.context['request'].user
        if not value.participants.filter(pk=user.pk).exists():
            raise ValidationError('You must be a participant in the conversation to post messages.')
        return value

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.StringRelatedField(many=True, read_only=True)
    items = serializers.PrimaryKeyRelatedField(many=True, queryset=Item.objects.all(), required=False)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Convversation
        fields = [
            'id',
            'participants',
            'items',
            'created_at',
            'updated_at',
            'messages',
        ]
        read_only_fields = ['id', 'participants', 'created_at', 'updated_at']


class CreateConversationSerializer(serializers.ModelSerializer):
    recipient_id = serializers.UUIDField(write_only=True)
    item_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Convversation
        fields = ['recipient_id', 'item_id']

    def validate_recipient_id(self, value):
        user = self.context['request'].user
        if value == user.id:
            raise ValidationError('Recipient must be different from the sender.')
        if not User.objects.filter(pk=value).exists():
            raise ValidationError('Recipient not found.')
        return value

    def validate_item_id(self, value):
        if not Item.objects.filter(pk=value).exists():
            raise ValidationError('Item not found.')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        recipient = User.objects.get(pk=validated_data['recipient_id'])

        conversation = Convversation.objects.create()
        conversation.participants.add(user, recipient)

        item_id = validated_data.get('item_id')
        if item_id:
            item = Item.objects.get(pk=item_id)
            conversation.items.add(item)

        return conversation
