from django.db import models
from django.conf import settings
from items.models import Item
import uuid


# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return sum(order_item.total_price for order_item in self.order_items.all())
    

    def __str__(self):
        return f"Order {self.id} - {self.item.name} by {self.buyer.email}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


    @property
    def total_price(self):
        return self.quantity * self.price
    
    def __str__(self):
        return f"{self.quantity} x {self.item.name} for Order {self.order.id}"



        'infevowhndchc vhz ,jbscjvhbdsjichbjskjcnxbjklXCNZbjkmlxNSKCBJVZd zbknlmXSNKbjvhcxnklmsdnkbjzhcxjknlmsncjxvbnzkmlXnckzjbjznkmLXzkcnjbjxnkzmlXZKNcjvbzklxcvn'