from rest_framework import serializers
from notifications.models import Notification, DeviceToken


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ['id', 'user', 'notification_type', 'title', 'body', 'is_read', 'data', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class DeviceTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceToken
        fields = ['id', 'user', 'token', 'platform', 'is_active', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

        