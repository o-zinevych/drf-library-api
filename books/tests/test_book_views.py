from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APIClient

from books.models import Book


BOOK_LIST_URL = reverse_lazy("books:book-list")


class BookAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.title = "Hamlet"
        self.author = "William Shakespeare"
        self.cover = "SOFT"
        self.inventory = 1
        self.daily_fee = 0.5
        self.book = Book.objects.create(
            title=self.title,
            author=self.author,
            cover=self.cover,
            inventory=self.inventory,
            daily_fee=self.daily_fee,
        )

        self.payload = {
            "title": "MacBeth",
            "author": self.author,
            "cover": self.cover,
            "inventory": self.inventory,
            "daily_fee": self.daily_fee,
        }

        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test1234"
        )
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@test.com", password="test1234"
        )

    def test_create_book_is_forbidden_when_not_admin(self):
        response = self.client.post(BOOK_LIST_URL, self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user)
        response = self.client.post(BOOK_LIST_URL, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_book_for_admin(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.post(BOOK_LIST_URL, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
