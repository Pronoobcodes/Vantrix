from rest_framework import serializers

from .models import Message, Convversation
from items.models import Item
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    offer_item_name = serializers.CharField(source='offer_item.name', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_username', 'content', 'is_offer', 'offer_price', 'offer_item', 'offer_item_name', 'offer_status', 'is_read', 'timestamp']
        read_only_fields = ['sender', 'timestamp', 'offer_status', 'is_read']


class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.StringRelatedField(many=True, source='participants', read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Convversation
        fields = ['id', 'participants', 'items', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['created_at', 'updated_at']

    def get_participants_usernames(self, obj):
        return [user.username for user in obj.participants.all()]

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-timestamp').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    

class CreateConversationSerializer(serializers.ModelSerializer):
    recipient_id = serializers.IntegerField(write_only=True)
    item_id = serializers.IntegerField(write_only=True, required=False)

    def create(self, validated_data):
        user = self.context['request'].user
        recipient = User.objects.get(id=validated_data['recipient_id'])

        conversation = Convversation.objects.create()
        conversation.participants.add(user, recipient)

        if validated_data.get('item_id'):
            item = Item.objects.get(id=validated_data['item_id'])
            conversation.items.add(item)

        return conversation
    


