import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer


BORROWING_LIST_URL = reverse_lazy("borrowings:borrowing-list")


class BorrowingsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.book = Book.objects.create(
            title="Title",
            author="Author",
            cover="SOFT",
            inventory=5,
            daily_fee=0.5,
        )
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test1234"
        )
        self.another_user = get_user_model().objects.create_user(
            email="another_user@test.com", password="test1234"
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() + datetime.timedelta(days=14),
            book=self.book,
            user=self.user,
        )
        self.another_borrowing = Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() + datetime.timedelta(days=14),
            book=self.book,
            user=self.another_user,
        )

    def test_borrowings_list(self):
        queryset = Borrowing.objects.select_related("book", "user")
        serializer = BorrowingListSerializer(queryset, many=True)

        response = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data["results"])

    def test_borrowings_user_id_list_filter(self):
        serializer = BorrowingListSerializer([self.borrowing], many=True)
        response = self.client.get(BORROWING_LIST_URL, {"user_id": self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data["results"])

        another_user_serializer = BorrowingListSerializer(
            [self.another_borrowing], many=True
        )
        self.assertNotEqual(another_user_serializer.data, response.data["results"])
