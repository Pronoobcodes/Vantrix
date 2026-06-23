from django.db import models
from django.conf import settings


class Convversation(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    items = models.ManyToManyField('items.Item', blank=True, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id}"
    

class Message(models.Model):
    conversation = models.ForeignKey(Convversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_offer = models.BooleanField(default=False)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    offer_item = models.ForeignKey('items.Item', on_delete=models.SET_NULL, null=True, blank=True, related_name='offer_messages')
    offer_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message {self.id} from {self.sender.username} in Conversation {self.conversation.id}"
    

