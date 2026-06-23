from django.test import TestCase
from django.contrib.auth import get_user_model

from items.models import Category, Item
from orders.models import Order
from .models import Review


class ReviewSignalsTestCase(TestCase):
	def setUp(self):
		User = get_user_model()
		self.buyer = User.objects.create_user(email='buyer@example.com', password='pass', username='buyer')
		self.seller = User.objects.create_user(email='seller@example.com', password='pass', username='seller')

		self.category = Category.objects.create(name='Test')
		self.item = Item.objects.create(
			name='Test Item',
			description='desc',
			price=10.00,
			category=self.category,
			owner=self.seller,
			stock=1,
		)

		self.order = Order.objects.create(
			buyer=self.buyer,
			seller=self.seller,
			status='delivered',
			total_amount=10.00,
			shipping_address={"street": "1 Main St"},
		)

	def test_review_create_updates_user_rating(self):
		# buyer reviews seller
		Review.objects.create(
			reviewer=self.buyer,
			reviewed_user=self.seller,
			item=self.item,
			order=self.order,
			role='buyer',
			rating=4,
			comment='Good',
		)

		self.seller.refresh_from_db()
		self.assertEqual(self.seller.total_reviews, 1)
		self.assertAlmostEqual(float(self.seller.average_rating), 4.0)

	def test_review_delete_updates_user_rating(self):
		review = Review.objects.create(
			reviewer=self.buyer,
			reviewed_user=self.seller,
			item=self.item,
			order=self.order,
			role='buyer',
			rating=5,
			comment='Excellent',
		)

		# sanity check
		self.seller.refresh_from_db()
		self.assertEqual(self.seller.total_reviews, 1)

		# delete and verify updates
		review.delete()
		self.seller.refresh_from_db()
		self.assertEqual(self.seller.total_reviews, 0)
		self.assertAlmostEqual(float(self.seller.average_rating), 0.0)

