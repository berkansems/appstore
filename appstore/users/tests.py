"""
Test For User Model
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class UserModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'berkan@example.com'
        password = 'PASSWORD'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        sample_emails = [
            ['test1@example.com', 'test1@example.com'],
            ['test2@Example.com', 'test2@example.com'],
            ['test3@EXAMPLE.com', 'test3@example.com'],
            ['Test4@example.com', 'Test4@example.com'],
            ['TEST5@example.com', 'TEST5@example.com'],
        ]
        # note that Test4@example.com and  TEST5@example.com with capital letters at first part is acceptable
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, password='PASSWORD')

            self.assertEqual(user.email, expected)

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'PASSWORD')

    def test_create_new_superuser(self):
        user = get_user_model().objects.create_superuser(email='test@example.com', password='PASSWORD')
        self.assertTrue(user.is_superuser, True)
        self.assertTrue(user.is_staff, True)


class UserAdminTests(TestCase):
    """Tests for django admin"""
    def setUp(self):
        """Create user and client."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Test User'
        )

    def test_users_lists(self):
        """Test that users are listed on page."""
        url = reverse('admin:users_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
        self.assertContains(res, self.admin_user.email)

    def test_edit_user_page(self):
        """Test the edit user page works."""
        url = reverse('admin:users_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works."""
        url = reverse('admin:users_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
