import datetime

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
)

BORROWING_LIST_URL = reverse_lazy("borrowings:borrowing-list")


def borrowing_detail_url(borrowing_id):
    return reverse_lazy("borrowings:borrowing-detail", args=[borrowing_id])


class BorrowingsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.today = datetime.date.today()
        self.valid_expected_return_date = datetime.date.today() + datetime.timedelta(
            days=14
        )
        self.initial_inventory = 5
        self.book = Book.objects.create(
            title="Title",
            author="Author",
            cover="SOFT",
            inventory=self.initial_inventory,
            daily_fee=0.5,
        )

        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test1234"
        )
        self.another_user = get_user_model().objects.create_user(
            email="another_user@test.com", password="test1234"
        )
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@test.com", password="test1234"
        )

        self.borrowing = Borrowing.objects.create(
            borrow_date=self.today,
            expected_return_date=self.valid_expected_return_date,
            book=self.book,
            user=self.user,
        )
        self.another_borrowing = Borrowing.objects.create(
            borrow_date=self.today,
            expected_return_date=self.valid_expected_return_date,
            actual_return_date=self.today,
            book=self.book,
            user=self.another_user,
        )

    def test_borrowings_list_returns_current_user_borrowings(self):
        self.client.force_authenticate(self.user)
        queryset = Borrowing.objects.select_related("book", "user").filter(
            user=self.user
        )
        serializer = BorrowingListSerializer(queryset, many=True)

        response = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data["results"])

    def test_borrowings_list_returns_all_borrowings_for_admin_users(self):
        self.client.force_authenticate(self.admin_user)
        queryset = Borrowing.objects.select_related("book", "user")
        serializer = BorrowingListSerializer(queryset, many=True)

        response = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data["results"])

    def test_borrowings_user_id_list_filter(self):
        self.client.force_authenticate(self.admin_user)
        serializer = BorrowingListSerializer([self.borrowing], many=True)

        response = self.client.get(BORROWING_LIST_URL, {"user_id": self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data["results"])

        another_user_serializer = BorrowingListSerializer(
            [self.another_borrowing], many=True
        )
        self.assertNotEqual(another_user_serializer.data, response.data["results"])

    def test_borrowings_is_active_true_list_filter(self):
        self.client.force_authenticate(self.user)
        queryset = Borrowing.objects.select_related("book", "user").filter(
            Q(actual_return_date__isnull=True), user=self.user
        )
        serializer = BorrowingListSerializer(queryset, many=True)

        response = self.client.get(BORROWING_LIST_URL, {"is_active": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data["results"])

    def test_borrowings_is_active_false_list_filter(self):
        self.client.force_authenticate(self.user)
        queryset = Borrowing.objects.select_related("book", "user").filter(
            Q(actual_return_date__isnull=False), user=self.user
        )
        serializer = BorrowingListSerializer(queryset, many=True)

        response = self.client.get(BORROWING_LIST_URL, {"is_active": "false"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data["results"])

    def test_applying_two_filters_to_borrowing_list(self):
        self.client.force_authenticate(self.admin_user)
        queryset = Borrowing.objects.select_related("book", "user").filter(
            Q(actual_return_date__isnull=True), user_id=self.user.id
        )
        serializer = BorrowingListSerializer(queryset, many=True)

        response = self.client.get(
            BORROWING_LIST_URL, {"user_id": self.user.id, "is_active": "true"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data["results"])

    def test_borrowing_detail(self):
        self.client.force_authenticate(self.user)
        serializer = BorrowingDetailSerializer(self.borrowing)
        response = self.client.get(borrowing_detail_url(self.borrowing.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_borrowing_create_serializer_borrow_date_validation(self):
        invalid_payload = {
            "borrow_date": self.today + datetime.timedelta(days=1),
            "expected_return_date": self.valid_expected_return_date,
            "actual_return_date": self.today,
            "book": self.book.id,
        }

        serializer = BorrowingCreateSerializer(data=invalid_payload)
        self.assertFalse(serializer.is_valid())

        self.client.force_authenticate(self.user)
        response = self.client.post(BORROWING_LIST_URL, invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("borrow_date", response.data)

    def test_borrowing_create_serializer_expected_return_date_validation(self):
        invalid_payload = {
            "borrow_date": self.today,
            "expected_return_date": self.today - datetime.timedelta(days=1),
            "actual_return_date": self.today,
            "book": self.book.id,
        }

        serializer = BorrowingCreateSerializer(data=invalid_payload)
        self.assertFalse(serializer.is_valid())

        self.client.force_authenticate(self.user)
        response = self.client.post(BORROWING_LIST_URL, invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("expected_return_date", response.data)

    def test_borrowing_create_serializer_actual_return_date_validation(self):
        invalid_payload = {
            "borrow_date": self.today,
            "expected_return_date": self.valid_expected_return_date,
            "actual_return_date": self.today + datetime.timedelta(days=1),
            "book": self.book.id,
        }

        serializer = BorrowingCreateSerializer(data=invalid_payload)
        self.assertFalse(serializer.is_valid())

        self.client.force_authenticate(self.user)
        response = self.client.post(BORROWING_LIST_URL, invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("actual_return_date", response.data)

    def test_borrowing_create_serializer_zero_inventory_validation(self):
        zero_inventory_book = Book.objects.create(
            title="Another Title",
            author="Author",
            cover="SOFT",
            inventory=0,
            daily_fee=0.5,
        )
        invalid_payload = {
            "borrow_date": self.today,
            "expected_return_date": self.valid_expected_return_date,
            "actual_return_date": self.today,
            "book": zero_inventory_book.id,
        }

        serializer = BorrowingCreateSerializer(data=invalid_payload)
        self.assertFalse(serializer.is_valid())

        self.client.force_authenticate(self.user)
        response = self.client.post(BORROWING_LIST_URL, invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("book_inventory", response.data)

    def test_borrowing_creation_subtracts_1_from_book_inventory(self):
        payload = {
            "borrow_date": self.today,
            "expected_return_date": self.valid_expected_return_date,
            "actual_return_date": "",
            "book": self.book.id,
        }

        self.client.force_authenticate(self.user)
        response = self.client.post(BORROWING_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, self.initial_inventory - 1)

    def test_borrowing_has_current_user_assigned_when_created(self):
        payload = {
            "borrow_date": self.today,
            "expected_return_date": self.valid_expected_return_date,
            "actual_return_date": "",
            "book": self.book.id,
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(BORROWING_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_borrowing = Borrowing.objects.get(pk=response.data["id"])
        self.assertEqual(new_borrowing.user, self.user)
