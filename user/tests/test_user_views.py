from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APIClient

import user

USER_URL = reverse_lazy("user:manage")


class UserAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = "test_email@test.com"
        self.password = "test_password1234"
        self.user = get_user_model().objects.create_user(
            email="another_user@test.com", password=self.password
        )

    def test_user_create_with_encrypted_password(self):
        payload = {"email": self.email, "password": self.password}
        response = self.client.post(reverse_lazy("user:register"), data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(pk=response.data["id"])
        self.assertNotEqual(payload["password"], user.password)
        self.assertTrue(user.check_password(payload["password"]))

    def test_user_retrieves_their_own_account(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(USER_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.pk)

    def test_user_password_update_is_encrypted(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch(USER_URL, {"password": "<PASSWORD>"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.password, self.user.password)
        self.assertTrue(self.user.check_password("<PASSWORD>"))

    def test_user_delete_method_is_not_allowed(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(USER_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
