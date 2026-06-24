from django.db.models.signals import post_save
from django.dispatch import receiver

from messages.models import Message
from orders.models import Order
from reviews.models import Review


@receiver(post_save, sender=Message)
def message_notification(sender, instance, created, **kwargs):
    if not created:
        return
    # Import task lazily to avoid import-time side effects
    from .tasks import send_push_notification_task

    recipients = instance.conversation.participants.exclude(id=instance.sender.id)
    for user in recipients:
        send_push_notification_task.delay(
            str(user.id),
            "new_message",
            "New Message",
            f"{instance.sender.username} sent you a message",
            {"conversation_id": str(instance.conversation.id)},
        )


@receiver(post_save, sender=Order)
def order_notification(sender, instance, **kwargs):
    from .tasks import send_push_notification_task

    # Notify the buyer about order updates
    if instance.buyer:
        send_push_notification_task.delay(
            str(instance.buyer.id),
            "order_update",
            "Order Updated",
            f"Order is now {instance.status}",
            {"order_id": str(instance.id)},
        )


@receiver(post_save, sender=Review)
def review_notification(sender, instance, created, **kwargs):
    if not created:
        return
    from .tasks import send_push_notification_task

    if instance.reviewed_user:
        send_push_notification_task.delay(
            str(instance.reviewed_user.id),
            "review",
            "New Review",
            f"{instance.reviewer.username} left a review",
            {"rating": str(instance.rating)},
        )
