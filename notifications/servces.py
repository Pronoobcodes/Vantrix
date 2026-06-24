from firebase_admin import messaging, credentials

from .models import Notification, DeviceToken


def create_notification(user, notification_type, title, body, data=None):
    """
    Create a new notification for a user.
    """
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        body=body,
        data=data or {}
    )
    return notification


def send_push_notification(device_token, title, body, data=None):
    """
    Send a push notification to a device using Firebase Cloud Messaging.
    """
    tokens = DeviceToken.objects.filter(token=device_token, is_active=True).first()

    for token in tokens:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token.token,
            data=data or {}
        )
        response = messaging.send(message)
    return response


def send_notification_to_user(user, notification_type, title, body, data=None):
    """
    Create a notification and send a push notification to all active device tokens of the user.
    """
    # Create the notification in the database
    notification = create_notification(user, notification_type, title, body, data)

    # Send push notifications to all active device tokens of the user
    device_tokens = DeviceToken.objects.filter(user=user, is_active=True)
    for device_token in device_tokens:
        send_push_notification(device_token.token, title, body, data)

    return notification


