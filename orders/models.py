from django.db import models
from django.conf import settings
import uuid

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("disputed", "Disputed"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="purchases"
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sales"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.JSONField()   # {street, city, state, zip, country}
    tracking_number = models.CharField(max_length=100, blank=True)
    logistics_partner = models.CharField(max_length=100, blank=True)
    buyer_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} — {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey("items.Item", on_delete=models.SET_NULL, null=True)
    item_title = models.CharField(max_length=200)   # snapshot at time of purchase
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(default=1)


class Escrow(models.Model):
    STATUS_CHOICES = [
        ("holding", "Holding"),
        ("released", "Released"),
        ("refunded", "Refunded"),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="escrow")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="holding")
    held_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Escrow for order {self.order.id} — {self.status}"