from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Order, App
from .serializers import OrderSerializer
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient


ORDERS_URL = reverse('order:order-list')


def detail_url(order_id):
    """Create and return a order detail URL."""
    return reverse('order:order-detail', args=[order_id])


# Helper functions to create data for testing
def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


def create_app(owner, **kwargs):
    app_params = {
        'title': 'Test App',
        'description': 'App description',
        'price': Decimal('10.00'),
        'verification_status': App.STATUS_VERIFIED
    }
    app_params.update(kwargs)
    return App.objects.create(**app_params, owner=owner)


def create_order(owner, app, **kwargs):
    order_params = {
        'owner': owner,
        'app': app,
    }
    order_params.update(kwargs)
    return Order.objects.create(**order_params)


class OrderSerializerTestCase(APITestCase):
    """Test for Order Serializer."""

    def setUp(self):
        """Create a user and an app for the test."""
        self.user = create_user(email="user@example.com", password="password123")
        self.client.force_authenticate(user=self.user)
        self.app = create_app(owner=self.user)

    def test_order_serializer_valid(self):
        """Test that the Order serializer works with valid data."""
        order_data = {
            'app': self.app.id,
        }
        serializer = OrderSerializer(data=order_data)
        self.assertTrue(serializer.is_valid())
        order = serializer.save(owner=self.user)  # `owner` is automatically set
        self.assertEqual(order.owner, self.user)
        self.assertEqual(order.app, self.app)

    def test_order_serializer_invalid(self):
        """Test that the Order serializer fails with invalid data."""
        order_data = {
            'app': None,  # Missing app
        }
        serializer = OrderSerializer(data=order_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('app', serializer.errors)


class OrderAPITests(APITestCase):
    """Test Order APIs."""

    def setUp(self):
        """Create a user and an app for the API tests."""
        self.user = create_user(email="user@example.com", password="password123")
        self.client.force_authenticate(user=self.user)
        self.app = create_app(owner=self.user)
        self.order = create_order(owner=self.user, app=self.app)

    def test_create_order(self):
        """Test creating a new order via the API."""
        # Ensure there's no existing order for this app and user
        Order.objects.filter(owner=self.user, app=self.app).delete()
        payload = {
            'app': self.app.id,
        }
        response = self.client.post(ORDERS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the order is created correctly
        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.app.id, self.app.id)
        self.assertEqual(order.owner, self.user)
        self.assertNotEqual(order.purchase_date, '2025-01-01')  # purchase_date is not changeable

    def test_get_order_detail(self):
        """Test getting order details via the API."""
        url = detail_url(self.order.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response matches the expected serializer data
        serializer = OrderSerializer(self.order)
        self.assertEqual(response.data, serializer.data)

    def test_order_unauthorized(self):
        """Test that an unauthenticated user cannot create or retrieve an order."""
        self.client.logout()
        payload = {
            'app': self.app.id,
        }
        response = self.client.post(ORDERS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_delete_own_order(self):
        """Test that the owner can delete their own order."""
        url = detail_url(self.order.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_other_user_cannot_delete_order(self):
        """Test that a user cannot delete another user's order."""
        other_user = create_user(email="other@example.com", password="password123")
        self.client.force_authenticate(user=other_user)

        url = detail_url(self.order.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Ensure the order still exists
        self.assertTrue(Order.objects.filter(id=self.order.id).exists())


class AppPurchasabilityTest(TestCase):

    def setUp(self):
        """Set up the test environment: create a user and an app."""
        self.client = APIClient()
        self.user = create_user(email="user@example.com", password="password123")
        self.client.force_authenticate(user=self.user)

        # Create apps with different verification statuses
        self.app_verified = App.objects.create(
            title="Verified App",
            description="This app is verified.",
            price=Decimal('10.00'),
            owner=self.user,
            verification_status=App.STATUS_VERIFIED  # Verified app
        )

        self.app_pending = App.objects.create(
            title="Pending App",
            description="This app is pending verification.",
            price=Decimal('10.00'),
            owner=self.user,
            verification_status=App.STATUS_PENDING  # Pending app
        )

    def test_create_order_for_verified_app(self):
        """Test that an order can be created for a verified app."""
        payload = {
            'app': self.app_verified.id,
        }
        response = self.client.post(ORDERS_URL, payload)

        # Check that the order is created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.app.id, self.app_verified.id)
        self.assertEqual(order.owner, self.user)

    def test_create_order_for_pending_app(self):
        """Test that an order cannot be created for a pending app."""
        payload = {
            'app': self.app_pending.id,
        }
        response = self.client.post(ORDERS_URL, payload)

        # Ensure the response status is 400 (Bad Request) due to the app not being verified
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that no order was created
        self.assertFalse(Order.objects.filter(app=self.app_pending).exists())
