from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APIClient


class UserAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = "test_email@test.com"
        self.password = "test_password1234"

    def test_user_create_with_encrypted_password(self):
        payload = {"email": self.email, "password": self.password}
        response = self.client.post(reverse_lazy("user:register"), data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(pk=response.data["id"])
        self.assertNotEqual(payload["password"], user.password)
        self.assertTrue(user.check_password(payload["password"]))
