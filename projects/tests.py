import json
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.test import Client
from .models import *


def create_user():
    user_payload = {
        'first_name': 'Muntasir',
        'last_name': 'Rahman',
        'username': 'raficsedu',
        'email': 'raficsedu@gmail.com',
        'password': make_password('Test1234')
    }
    return User.objects.create(**user_payload)


def authenticate(client):
    url = reverse('authenticate')
    payload = {
        'email': 'raficsedu@gmail.com',
        'password': 'Test1234'
    }
    return client.post(url, data=json.dumps(payload), content_type="application/json")


class ProjectTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create default user and login
        cls.user = create_user()
        client = Client()
        response = authenticate(client)
        cls.token = response.data['results']['token']['access']

    def setUp(self):
        # Login and get token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        # Project payload
        self.url = reverse('project')
        self.project_payload = {
            'title': 'Online timelog project',
            'description': 'User will be able to log their time on project'
        }
        self.project = Project.objects.create(user=self.user, **self.project_payload)

    def test_create_invalid_project(self):
        self.project_payload['title'] = ''
        response = self.client.post(self.url, data=json.dumps(self.project_payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_create_valid_project(self):
        response = self.client.post(self.url, data=json.dumps(self.project_payload), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['results']['id'], 2)

    def test_update_valid_project(self):
        self.url = reverse('project_by_id', args=[self.project.id])
        self.project_payload['status'] = 0
        response = self.client.put(self.url, data=json.dumps(self.project_payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results']['status'], 0)

        # Check from DB
        self.project.refresh_from_db()
        self.assertEqual(response.data['results']['status'], 0)

    def test_delete_project(self):
        self.url = reverse('project_by_id', args=[self.project.id])
        response = self.client.delete(self.url, data={}, content_type="application/json")
        self.assertEqual(response.status_code, 204)
