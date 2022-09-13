import json
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


def create_user():
    user_payload = {
        'first_name': 'Muntasir',
        'last_name': 'Rahman',
        'username': 'raficsedu',
        'email': 'raficsedu@gmail.com',
        'password': make_password('Test1234')
    }
    return User.objects.create(**user_payload)


class UserTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create default user
        cls.user = create_user()

    def setUp(self):
        self.url = reverse('register')
        self.payload = {
            'username': 'testuser',
            'email': 'testuser@gmail.com',
            'password': 'Test1234'
        }

    def test_required_field(self):
        for key in self.payload:
            self.payload[key] = ''
            response = self.client.post(self.url, data=json.dumps(self.payload), content_type="application/json")
            self.assertEqual(response.status_code, 400)

    def test_duplicate_email(self):
        self.payload['email'] = 'raficsedu@gmail.com'
        response = self.client.post(self.url, data=json.dumps(self.payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_duplicate_username(self):
        self.payload['username'] = 'raficsedu'
        response = self.client.post(self.url, data=json.dumps(self.payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_password_length(self):
        self.payload['password'] = 'Test123'
        response = self.client.post(self.url, data=json.dumps(self.payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_create_valid_user(self):
        response = self.client.post(self.url, data=json.dumps(self.payload), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['results']['id'], 2)


class AuthenticationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create default user
        cls.user = create_user()

    def setUp(self):
        self.url = reverse('authenticate')
        self.payload = {
            'email': 'raficsedu@gmail.com',
            'password': 'Test1234'
        }

    def test_required_field(self):
        self.payload['email'] = ''
        self.payload['password'] = ''
        response = self.client.post(self.url, data=json.dumps(self.payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_wrong_auth(self):
        self.payload['password'] = 'Test4321'
        response = self.client.post(self.url, data=json.dumps(self.payload), content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_valid_auth(self):
        response = self.client.post(self.url, data=json.dumps(self.payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results']['id'], 1)
