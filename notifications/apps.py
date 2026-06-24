from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = 'notifications'

    def ready(self):
        # Import signal handlers to wire them up when app is ready
        try:
            import notifications.signals  # noqa: F401
        except Exception:
            pass
