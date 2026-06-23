from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Review(models.Model):
    REVIEWER_ROLES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    ]

    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    reviewed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received')
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='reviews')
    role = models.CharField(max_length=10, choices=REVIEWER_ROLES)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('reviewer', 'order')

    def __str__(self):
        return f"{self.reviewer.username} reviewed {self.reviewed_user.username} for {self.item.name} - Rating: {self.rating}"