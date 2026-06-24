from celery import shared_task
from django.contrib.auth import get_user_model

from .servces import send_notification_to_user


@shared_task
def send_push_notification_task(user_id, notification_type, title, body, data=None):
    user_model = get_user_model()
    try:
        user = user_model.objects.get(pk=user_id)
    except user_model.DoesNotExist:
        return None

    send_notification_to_user(user, notification_type, title, body, data)
