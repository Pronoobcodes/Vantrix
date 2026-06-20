from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from items.models import Category, Item
from orders.models import Order
from payments.models import Payment

User = get_user_model()


class PaymentsAppTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            email='seller@example.com',
            username='seller',
            password='pass1234'
        )
        self.buyer = User.objects.create_user(
            email='buyer@example.com',
            username='buyer',
            password='pass1234'
        )

        self.category = Category.objects.create(name='Test Category')
        self.item = Item.objects.create(
            name='Sample Item',
            description='A sample product',
            price=Decimal('10.00'),
            category=self.category,
            owner=self.seller,
            stock=10,
        )

        self.order = Order.objects.create(
            buyer=self.buyer,
            seller=self.seller,
            shipping_address={
                'street': '123 Main St',
                'city': 'Testville',
                'state': 'TX',
                'zip': '75001',
                'country': 'USA',
            },
            total_amount=Decimal('20.00'),
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.buyer)

    @patch('payments.services.PaystackService.initialize_payment')
    def test_initialize_payment_creates_payment(self, mock_initialize_payment):
        mock_initialize_payment.return_value = {
            'status': True,
            'data': {
                'reference': 'payref_123',
                'authorization_url': 'https://paystack.com/authorize',
            },
        }

        response = self.client.post(
            '/vantrix/payments/initialize/',
            {'order_id': str(self.order.id)},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['authorization_url'], 'https://paystack.com/authorize')

        payment = Payment.objects.get(order=self.order)
        self.assertEqual(payment.user, self.buyer)
        self.assertEqual(payment.gateway_reference, 'payref_123')
        self.assertEqual(payment.status, 'PENDING')
        self.assertEqual(payment.amount, self.order.total_amount)

    @patch('payments.services.PaystackService.verify_payment')
    def test_verify_payment_updates_order_status(self, mock_verify_payment):
        payment = Payment.objects.create(
            user=self.buyer,
            order=self.order,
            gateway='Paystack',
            gateway_reference='payref_123',
            amount=self.order.total_amount,
            currency='NGN',
            reference='payment-ref-123',
        )

        mock_verify_payment.return_value = {
            'status': True,
            'data': {
                'reference': 'payment-ref-123',
                'status': 'success',
            },
        }

        response = self.client.get('/vantrix/payments/verify/', {'reference': payment.reference})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(payment.status, 'COMPLETED')
        self.assertEqual(self.order.status, 'paid')

    @patch('payments.services.PaystackService.verify_payment')
    def test_webhook_updates_existing_payment(self, mock_verify_payment):
        payment = Payment.objects.create(
            user=self.buyer,
            order=self.order,
            gateway='Paystack',
            gateway_reference='payref_123',
            amount=self.order.total_amount,
            currency='NGN',
            reference='payment-ref-123',
        )

        mock_verify_payment.return_value = {
            'status': True,
            'data': {
                'reference': 'payment-ref-123',
                'status': 'success',
            },
        }

        self.client.force_authenticate(user=None)
        response = self.client.post(
            '/vantrix/payments/webhook/',
            {'data': {'reference': payment.reference}},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(payment.status, 'COMPLETED')
        self.assertEqual(self.order.status, 'paid')
