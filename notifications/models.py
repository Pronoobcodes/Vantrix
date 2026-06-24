from django.db import models
from django.conf import settings

# Create your models here.


class Notification(models.Model):
    TYPE_CHOICES = [
        ('new_message', 'New Message'),
        ('offer', 'Offer'),
        ('order_update', 'Order Update'),
        ('price_drop', 'Price Drop'),
        ('new_listing', 'New Listing'),
        ('review', 'Review'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    data = models.JSONField(blank=True, null=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class DeviceToken(models.Model):
    PLATFORM_CHOICES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='device_tokens')
    token = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=30, choices=PLATFORM_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
