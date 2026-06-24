from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.models import Notification, DeviceToken
from notifications.serializers import NotificationSerializer, DeviceTokenSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    

class NotificationDetailView(generics.RetrieveAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    

class MarkNotificationAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({'status': 'success', 'message': 'Notification marked as read.'})
        except Notification.DoesNotExist:
            return Response({'status': 'error', 'message': 'Notification not found.'}, status=404)
        

class MarkAllNotificationsAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications.update(is_read=True)
        return Response({'status': 'success', 'message': 'All notifications marked as read.'})
    

class NotificationCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': unread_count})
    

class RegisterDeviceTokenView(generics.CreateAPIView):
    serializer_class = DeviceTokenSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DeleteDeviceTokenView(generics.DestroyAPIView):
    serializer_class = DeviceTokenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DeviceToken.objects.filter(user=self.request.user)
    

