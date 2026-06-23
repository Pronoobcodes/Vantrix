from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review


def update_user_rating(user):
    reviews = Review.objects.filter(reviewed_user=user)
    avg = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    user.average_rating = avg
    user.total_reviews = reviews.count()
    user.save(update_fields=['average_rating', 'total_reviews'])


@receiver(post_save, sender=Review)
def review_created(sender, instance, **kwargs):
    update_user_rating(instance.reviewed_user)


@receiver(post_delete, sender=Review)
def review_deleted(sender, instance, **kwargs):
    update_user_rating(instance.reviewed_user)
