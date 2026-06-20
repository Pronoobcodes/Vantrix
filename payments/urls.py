from django.urls import path
from .views import InitializePaymentView, VerifyPaymentView, PaymentListView, PaystackWebhookView


urlpatterns = [
    path('initialize/', InitializePaymentView.as_view(), name='initialize-payment'),
    path('verify/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('list/', PaymentListView.as_view(), name='payment-list'),
    path('webhook/', PaystackWebhookView.as_view(), name='paystack-webhook'),
]

