from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Message, Convversation
from .serializers import MessageSerializer, ConversationSerializer, CreateConversationSerializer
from .permissions import IsConversationParticipant


class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Convversation.objects.filter(participants=self.request.user).prefetch_related('participants', 'messages')

    def perform_create(self, serializer):
        serializer.save()


class ConversationDetailView(generics.RetrieveAPIView):
    queryset = Convversation.objects.all().prefetch_related('participants', 'messages')
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsConversationParticipant]


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    def post(self, request, conversation_id):
        conversation = generics.get_object_or_404(Convversation, id=conversation_id)
        self.check_object_permissions(request, conversation)

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, conversation=conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class SendOfferView(APIView):
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    def post(self, request, conversation_id):
        conversation = generics.get_object_or_404(Convversation, id=conversation_id)
        self.check_object_permissions(request, conversation)

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, conversation=conversation, is_offer=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AcceptOfferView(APIView):
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    def post(self, request, message_id):
        message = generics.get_object_or_404(Message, id=message_id, is_offer=True)
        conversation = message.conversation
        self.check_object_permissions(request, conversation)

        if message.offer_status != 'pending':
            return Response({'detail': 'Offer has already been processed.'}, status=status.HTTP_400_BAD_REQUEST)

        message.offer_status = 'accepted'
        message.save()

        return Response({'detail': 'Offer accepted.'}, status=status.HTTP_200_OK)
    

class RejectOfferView(APIView):
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    def post(self, request, message_id):
        message = generics.get_object_or_404(Message, id=message_id, is_offer=True)
        conversation = message.conversation
        self.check_object_permissions(request, conversation)

        if message.offer_status != 'pending':
            return Response({'detail': 'Offer has already been processed.'}, status=status.HTTP_400_BAD_REQUEST)

        message.offer_status = 'rejected'
        message.save()

        return Response({'detail': 'Offer rejected.'}, status=status.HTTP_200_OK)
    

class MarkMessageReadView(APIView):
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    def post(self, request, message_id):
        message = generics.get_object_or_404(Message, id=message_id)
        conversation = message.conversation
        self.check_object_permissions(request, conversation)

        if message.sender == request.user:
            return Response({'detail': 'Cannot mark your own message as read.'}, status=status.HTTP_400_BAD_REQUEST)

        message.is_read = True
        message.save()

        return Response({'detail': 'Message marked as read.'}, status=status.HTTP_200_OK)
    

class UnreadMessagesCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        conversation = generics.get_object_or_404(Convversation, id=conversation_id)
        if not conversation.participants.filter(id=request.user.id).exists():
            return Response({'detail': 'Not a participant of this conversation.'}, status=status.HTTP_403_FORBIDDEN)

        unread_count = conversation.messages.filter(is_read=False).exclude(sender=request.user).count()
        return Response({'unread_count': unread_count}, status=status.HTTP_200_OK)


class DeleteMessageView(APIView):
    """Delete a message by ID with validation and permission checks."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, message_id):
        try:
            # Retrieve the message and verify it exists
            message = generics.get_object_or_404(Message, id=message_id)
            conversation = message.conversation
            
            # Check if user is a participant of the conversation
            if not conversation.participants.filter(id=request.user.id).exists():
                return Response(
                    {'detail': 'You are not a participant of this conversation.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Only allow the sender to delete their own message
            if message.sender != request.user:
                return Response(
                    {'detail': 'You can only delete your own messages.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Delete the message
            message_id = message.id
            message.delete()
            
            return Response(
                {'detail': f'Message {message_id} deleted successfully.'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {'detail': f'An error occurred while deleting the message: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateMessageView(APIView):
    """Update a message by ID with validation and permission checks."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, message_id):
        try:
            # Retrieve the message and verify it exists
            message = generics.get_object_or_404(Message, id=message_id)
            conversation = message.conversation
            
            # Check if user is a participant of the conversation
            if not conversation.participants.filter(id=request.user.id).exists():
                return Response(
                    {'detail': 'You are not a participant of this conversation.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Only allow the sender to update their own message
            if message.sender != request.user:
                return Response(
                    {'detail': 'You can only update your own messages.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Validate and update the message
            serializer = MessageSerializer(message, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'detail': f'An error occurred while updating the message: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AddMessageView(APIView):
    """Add a new message to a conversation with full validation."""
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    def post(self, request, conversation_id):
        try:
            # Retrieve and verify conversation exists
            conversation = generics.get_object_or_404(Convversation, id=conversation_id)
            self.check_object_permissions(request, conversation)
            
            # Validate input data
            if 'content' not in request.data or not request.data['content'].strip():
                return Response(
                    {'detail': 'Message content is required and cannot be empty.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create message with serializer validation
            serializer = MessageSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(sender=request.user, conversation=conversation)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'detail': f'An error occurred while adding the message: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )