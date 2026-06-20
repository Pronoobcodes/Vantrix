from django.db import models
from django.conf import settings
import uuid

# Create your models here.


class Payment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
        ('CANCELED', 'Canceled')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payments')
    gateway = models.CharField(max_length=50, default='Paystack')
    gateway_reference = models.CharField(max_length=200, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='NGN')
    gateway_response = models.JSONField(default=dict)
    reference = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.reference}, {self.gateway} - {self.gateway_reference}"
    
    