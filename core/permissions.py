from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return getattr(obj, 'owner', None) == request.user or request.user.is_staff


class IsAuthenticatedAndOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and getattr(obj, 'owner', None) == request.user


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'owner', None) == request.user or request.user.is_staff


class IsConversationParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'participants'):
            return obj.participants.filter(id=request.user.id).exists()
        if hasattr(obj, 'conversation'):
            return obj.conversation.participants.filter(id=request.user.id).exists()
        return False


class IsMessageSender(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'sender', None) == request.user
