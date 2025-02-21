from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from apps.models import App


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


class AppStoreAppTestCase(TestCase):
    def setUp(self):
        params = {
            'email': 'test@gmail.com',
            'password': '<PASSWORD>',
            'name': 'sample name',
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
