from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    name = 'reviews'

    def ready(self):
        # Import signals to connect handlers
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
