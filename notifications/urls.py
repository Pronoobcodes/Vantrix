from django.urls import path

from .views import (
	NotificationListView,
	NotificationDetailView,
	NotificationCountView,
	MarkNotificationAsReadView,
	MarkAllNotificationsAsReadView,
	RegisterDeviceTokenView,
	DeleteDeviceTokenView,
)

urlpatterns = [
	path("", NotificationListView.as_view(), name="notifications"),
	path("<int:pk>/", NotificationDetailView.as_view(), name="notification-detail"),
	path("<int:pk>/read/", MarkNotificationAsReadView.as_view(), name="notification-read"),
	path("read-all/", MarkAllNotificationsAsReadView.as_view(), name="notification-read-all"),
	path("count/", NotificationCountView.as_view(), name="notification-count"),
	path("device/register/", RegisterDeviceTokenView.as_view(), name="device-register"),
	path("device/deactivate/", DeleteDeviceTokenView.as_view(), name="device-deactivate"),
]

