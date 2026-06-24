Vantrix
=======

A Django marketplace backend with apps for items, messaging, orders, payments, reviews, notifications, and users.

**Project Structure**
- **Root:** db.sqlite3 — local SQLite database (if present).
- **Entry point:** [manage.py](manage.py) — Django management utility.
- **Settings:** [Vantrix/settings.py](Vantrix/settings.py#L1-L200) — project settings and configuration.
- **Apps:**
- **Items:** app for marketplace items (`items`) — see [items/models.py](items/models.py#L1-L200).
- **Messages:** real-time conversations & messages — see [messages/models.py](messages/models.py#L1-L200).
- **Orders:** order lifecycle & order items — see [orders/models.py](orders/models.py#L1-L200).
- **Payments:** payment models and services — see [payments/services.py](payments/services.py#L1-L200).
- **Reviews:** reviews and ratings — see [reviews/models.py](reviews/models.py#L1-L200).
- **Notifications:** push & DB notifications — see [notifications/apps.py](notifications/apps.py#L1-L40) and newly added files below.
- **Users:** custom user model and profiles — see [users/models.py](users/models.py#L1-L200).

**Notifications (recent additions)**
- **URL routes:** [notifications/urls.py](notifications/urls.py#L1-L30)
- **Signals:** [notifications/signals.py](notifications/signals.py#L1-L200) — enqueues notification tasks on message/order/review events.
- **Celery task:** [notifications/tasks.py](notifications/tasks.py#L1-L200) — background task that calls the notification service.
- **Service:** [notifications/servces.py](notifications/servces.py#L1-L200) — creates DB notifications and sends FCM push messages. (Note: file named `servces.py` in the repo.)
- **Firebase credentials:** [notifications/firebase-service-account.json](notifications/firebase-service-account.json)

**Setup**
- Create and activate a Python virtual environment (recommended Python 3.10+).

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate
```

- Install dependencies:

```bash
pip install -r requirements.txt
```

- Apply migrations and create a superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
```

- Run the development server:

```bash
python manage.py runserver
```

- Start a Celery worker (if using background tasks). Set your broker (e.g., Redis URL) in settings before starting:

```bash
# Example (from project root)
celery -A Vantrix worker -l info
```

**Testing**
- Run Django tests:

```bash
python manage.py test
```

**Notes**
- The notifications service uses Firebase Cloud Messaging. Ensure `notifications/firebase-service-account.json` is present and environment configured for Firebase.
- Celery/Redis (or another broker) is recommended for background delivery of push notifications. Without Celery, signals currently enqueue tasks; you can add a synchronous fallback if you need immediate sending in non-Celery environments.

**Next steps**
- Verify `INSTALLED_APPS` includes `notifications.apps.NotificationsConfig` (or `notifications`).
- Configure a Celery broker (Redis) and start a worker to process queued notification tasks.

If you want, I can: add a synchronous fallback, update the misnamed `servces.py` to `services.py`, or add a minimal test that asserts notifications are created on message creation.
