from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookListSerializer, BookSerializer

BOOK_LIST_URL = reverse_lazy("books:book-list")


def book_detail_url(book_id):
    return reverse_lazy("books:book-detail", args=[book_id])


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

    def test_book_list_correct_and_available_to_anyone(self):
        Book.objects.create(**self.payload)
        books = Book.objects.all()
        serializer = BookListSerializer(books, many=True)
        response = self.client.get(BOOK_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data["results"])

    def test_book_detail_view_representation(self):
        serializer = BookSerializer(self.book)
        response = self.client.get(book_detail_url(self.book.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)
        self.assertEqual(self.cover.capitalize(), response.data["cover"])

    def test_book_update_is_forbidden_when_not_admin(self):
        response = self.client.put(book_detail_url(self.book.id), self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user)
        response = self.client.put(book_detail_url(self.book.id), self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.admin_user)
        response = self.client.put(book_detail_url(self.book.id), self.payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_book_destroy_is_forbidden_when_not_admin(self):
        response = self.client.delete(book_detail_url(self.book.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user)
        response = self.client.delete(book_detail_url(self.book.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.admin_user)
        response = self.client.delete(book_detail_url(self.book.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
