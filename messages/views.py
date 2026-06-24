from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Convversation, Message
from .serializers import (
    ConversationSerializer,
    CreateConversationSerializer,
    MessageCreateSerializer,
    MessageSerializer,
)
from core.permissions import IsConversationParticipant, IsMessageSender


class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    def get_queryset(self):
        return (
            Convversation.objects.filter(participants=self.request.user)
            .prefetch_related('participants', 'messages', 'items')
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateConversationSerializer
        return ConversationSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        serializer = MessageSerializer(conversation.messages.all(), many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Message.objects.select_related('conversation', 'sender', 'offer_item')
            .filter(conversation__participants=self.request.user)
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def get_permissions(self):
        if self.action in ['partial_update', 'destroy']:
            return [IsAuthenticated(), IsMessageSender()]
        if self.action in ['accept_offer', 'reject_offer', 'mark_read']:
            return [IsAuthenticated(), IsConversationParticipant()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def accept_offer(self, request, pk=None):
        message = self.get_object()
        if not message.is_offer:
            return Response({'detail': 'Message is not an offer.'}, status=status.HTTP_400_BAD_REQUEST)
        if message.offer_status != 'pending':
            return Response({'detail': 'Offer has already been processed.'}, status=status.HTTP_400_BAD_REQUEST)
        if message.sender == request.user:
            return Response({'detail': 'Sender cannot accept their own offer.'}, status=status.HTTP_403_FORBIDDEN)

        message.offer_status = 'accepted'
        message.save()
        return Response({'detail': 'Offer accepted.'})

    @action(detail=True, methods=['post'])
    def reject_offer(self, request, pk=None):
        message = self.get_object()
        if not message.is_offer:
            return Response({'detail': 'Message is not an offer.'}, status=status.HTTP_400_BAD_REQUEST)
        if message.offer_status != 'pending':
            return Response({'detail': 'Offer has already been processed.'}, status=status.HTTP_400_BAD_REQUEST)
        if message.sender == request.user:
            return Response({'detail': 'Sender cannot reject their own offer.'}, status=status.HTTP_403_FORBIDDEN)

        message.offer_status = 'rejected'
        message.save()
        return Response({'detail': 'Offer rejected.'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        if message.sender == request.user:
            return Response({'detail': 'Cannot mark your own message as read.'}, status=status.HTTP_400_BAD_REQUEST)

        message.is_read = True
        message.save()
        return Response({'detail': 'Message marked as read.'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        conversation_id = request.query_params.get('conversation_id')
        if not conversation_id:
            return Response(
                {'detail': 'conversation_id query parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation = get_object_or_404(
            Convversation,
            pk=conversation_id,
            participants=request.user,
        )
        unread_count = conversation.messages.filter(is_read=False).exclude(sender=request.user).count()
        return Response({'unread_count': unread_count})
