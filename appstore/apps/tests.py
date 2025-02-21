"""
Tests for apps APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.models import App
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from apps.serializers import AppSerializer, AppDetailSerializer


APPS_URL = reverse('app:app-list')

def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


def create_app(**kwargs):
    app_params = {
        'title': 'Test app title',
        'description': 'Test app description',
        'price': 19.99,
    }
    app_params.update(kwargs)
    return App.objects.create(**app_params)


def detail_url(app_id):
    """Create and return a app detail URL."""
    return reverse('app:app-detail', args=[app_id])


class AppStoreAppTestCase(TestCase):
    def setUp(self):
        params = {
            'email': 'test@gmail.com',
            'password': '<PASSWORD>',
            'name': 'sample name',
            'is_staff': True,
        }
        self.user = create_user(**params)
        self.app1 = App.objects.create(
            title="App 1",
            owner=self.user,
            price=10.0,
            verification_status=App.STATUS_PENDING,
        )
        self.app2 = App.objects.create(
            title="App 2",
            owner=self.user,
            price=15.0,
            verification_status=App.STATUS_PENDING,
        )

    def test_app_creation_with_default_values(self):
        """Test app creation with default values"""
        app = create_app(owner=self.user)
        self.assertEqual(app.title, 'Test app title')
        self.assertEqual(app.description, 'Test app description')
        self.assertEqual(app.price, 19.99)
        self.assertEqual(app.owner, self.user)

    def test_app_creation_with_custom_values(self):
        """Test app creation with custom values passed via kwargs"""
        custom_params = {
            'title': 'Custom app title',
            'description': 'Custom app description',
            'price': 29.99,
        }
        app = create_app(owner=self.user, **custom_params)
        self.assertEqual(app.title, 'Custom app title')
        self.assertEqual(app.description, 'Custom app description')
        self.assertEqual(app.price, 29.99)
        self.assertEqual(app.owner, self.user)

    def test_app_creation_with_invalid_price(self):
        """Test that invalid price value raises an error"""
        with self.assertRaises(ValidationError):
            create_app(owner=self.user, price="invalid_price")

    def test_multiple_apps_creation(self):
        """Test creating multiple apps and checking that they are saved properly"""
        self.assertEqual(App.objects.count(), 2)

    def test_verify_app_status_change(self):
        """test app's status can change"""
        self.assertEqual(self.app1.verification_status, App.STATUS_PENDING)

        self.app1.verification_status = App.STATUS_VERIFIED
        self.app2.verification_status = App.STATUS_REJECTED
        self.app1.save()
        self.app2.save()
        self.app1.refresh_from_db()
        self.app2.refresh_from_db()

        self.assertEqual(self.app1.verification_status, App.STATUS_VERIFIED)
        self.assertEqual(self.app2.verification_status, App.STATUS_REJECTED)

    def test_verified_date_on_app_status_change_to_verify(self):
        """Test the verified_date of an app when its status changes to verified."""
        self.app1.verification_status = App.STATUS_VERIFIED
        self.app2.verification_status = App.STATUS_REJECTED
        self.app1.save()
        self.app2.save()
        self.app1.refresh_from_db()
        self.app2.refresh_from_db()

        self.assertIsNotNone(self.app1.verified_date)
        self.assertIsNone(self.app2.verified_date)

    def test_verify_app_once(self):
        """Test that an app can only be verified once."""
        self.assertIsNone(self.app1.verified_date)

        # First verification should be successful
        self.app1.verify()
        self.assertEqual(self.app1.verification_status, App.STATUS_VERIFIED)
        self.assertIsNotNone(self.app1.verified_date)

        # Second verification attempt should not change the verified_date
        old_verified_date = self.app1.verified_date
        self.app1.verify()
        self.assertEqual(self.app1.verified_date, old_verified_date)  # Date should remain unchanged
        self.assertEqual(self.app1.verification_status, App.STATUS_VERIFIED)


class PublicAppsAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(APPS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAppApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(self.user)
        self.payload = {
            "title": "Test app title",
            "description": "Test app description",
            "price": Decimal('20.00'),
        }

    def test_retrieve_apps(self):
        """Test retrieving a list of apps."""
        create_app(owner=self.user)
        create_app(owner=self.user, title='Test app title 2')

        res = self.client.get(APPS_URL)

        apps = App.objects.all()
        serializer = AppSerializer(apps, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_apps_list_limited_to_user(self):
        """Test list of app is limited to authenticated user."""
        other_user = create_user(
            email='other@example.com',
            password='password123',
        )
        create_app(owner=other_user)
        create_app(owner=self.user, title='Test app title 2')

        res = self.client.get(APPS_URL)

        apps = App.objects.all()
        serializer = AppSerializer(apps, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_app_detail(self):
        """Test get app detail."""
        app = create_app(owner=self.user)

        url = detail_url(app.id)
        res = self.client.get(url)

        serializer = AppDetailSerializer(app)
        self.assertEqual(res.data, serializer.data)

    def test_create_app(self):
        """Test creating an app"""
        res = self.client.post(APPS_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        app = App.objects.get(id=res.data['id'])
        for k, v in self.payload.items():
            self.assertEqual(getattr(app, k), v)
        self.assertEqual(app.owner, self.user)

    def test_partial_update(self):
        """Test partial update of a app."""
        app = create_app(
            title='Sample app title',
            owner=self.user,
        )

        payload = {'title': 'New app title'}
        url = detail_url(app.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        app.refresh_from_db()
        self.assertEqual(app.title, payload['title'])

        self.assertEqual(app.owner, self.user)

    def test_full_update(self):
        """Test full update of app."""
        app = create_app(
            title='Sample app title',
            description='Sample app description.',
            owner=self.user,
        )

        payload = {
            'title': 'New app title',
            'description': 'New app description',
            'price': Decimal('2.50'),
        }
        url = detail_url(app.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        app.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(app, k), v)
        self.assertEqual(app.owner, self.user)


    def test_verification_status_update_is_impossible(self):
        """
        checks that even if verification_status is in the payload we can not update it.
        this is because verification_status is in the read_only_fields of the app AppSerializer
        """
        app = create_app(
            title='Sample app title',
            description='Sample app description.',
            owner=self.user,
        )

        payload = {
            'title': 'New app title',
            'description': 'New app description',
            'price': Decimal('2.50'),
            'verification_status': App.STATUS_REJECTED,
        }
        url = detail_url(app.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        the_app = App.objects.get(id=app.id)
        self.assertEqual(the_app.verification_status, App.STATUS_PENDING) # remained unchanged

    def test_update_user_returns_error(self):
        """Test changing the app owner results in an error. it is a read_only field."""
        new_user = create_user(email='user2@example.com', password='test123')
        app = create_app(owner=self.user)

        payload = {'owner': new_user.id}
        url = detail_url(app.id)
        self.client.patch(url, payload)

        app.refresh_from_db()
        self.assertEqual(app.owner, self.user)

    def test_delete_app(self):
        """Test deleting a app successful."""
        app = create_app(owner=self.user)

        url = detail_url(app.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(App.objects.filter(id=app.id).exists())

    def test_app_other_users_app_error(self):
        """Test trying to delete another users app gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        app = create_app(owner=new_user)

        url = detail_url(app.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(App.objects.filter(id=app.id).exists())