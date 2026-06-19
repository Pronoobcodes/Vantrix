from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from items.models import Category, Item
from orders.models import Order

User = get_user_model()


class OrdersAppTests(TestCase):
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

        self.client = APIClient()
        self.client.force_authenticate(user=self.buyer)

    def test_checkout_creates_order(self):
        payload = {
            'seller_id': str(self.seller.id),
            'shipping_address': {
                'street': '123 Main St',
                'city': 'Testville',
                'state': 'TX',
                'zip': '75001',
                'country': 'USA',
            },
            'items': [
                {'item_id': str(self.item.id), 'quantity': 2},
            ],
        }

        response = self.client.post('/vantrix/orders/checkout/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)

        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.buyer, self.buyer)
        self.assertEqual(order.seller, self.seller)
        self.assertEqual(order.total_amount, Decimal('20.00'))
        self.assertEqual(order.items.count(), 1)

    def test_buyer_and_seller_order_list_endpoints(self):
        order = Order.objects.create(
            buyer=self.buyer,
            seller=self.seller,
            shipping_address={
                'street': '123 Main St',
                'city': 'Testville',
                'state': 'TX',
                'zip': '75001',
                'country': 'USA',
            },
            total_amount=Decimal('10.00'),
        )

        response = self.client.get('/vantrix/orders/buyer/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], str(order.id))

        self.client.force_authenticate(user=self.seller)
        response = self.client.get('/vantrix/orders/seller/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], str(order.id))
