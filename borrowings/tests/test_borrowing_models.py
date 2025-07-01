import datetime
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from books.models import Book
from borrowings.models import Borrowing


class BorrowingModelTests(TestCase):
    def setUp(self):
        self.borrow_date = datetime.date.today()
        self.expected_return_date = self.borrow_date + datetime.timedelta(days=30)
        self.book = Book.objects.create(
            title="Title",
            author="Author",
            cover="SOFT",
            inventory=1,
            daily_fee=0.5,
        )
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test1234"
        )
        self.valid_borrowing = Borrowing.objects.create(
            borrow_date=self.borrow_date,
            expected_return_date=self.expected_return_date,
            book=self.book,
            user=self.user,
        )

    def test_borrowing_str(self):
        self.assertEqual(
            f"{self.book.title} due {self.expected_return_date}",
            str(self.valid_borrowing),
        )

    def test_is_active_property(self):
        self.assertTrue(self.valid_borrowing.is_active)

        inactive_borrowing = Borrowing.objects.create(
            borrow_date=self.borrow_date,
            expected_return_date=self.expected_return_date,
            actual_return_date=self.borrow_date,
            book=self.book,
            user=self.user,
        )
        self.assertFalse(inactive_borrowing.is_active)

    def test_borrowing_expected_return_date_validation(self):
        past_date = self.borrow_date - timedelta(days=3)
        with self.assertRaises(ValidationError):
            Borrowing.objects.create(
                borrow_date=self.borrow_date,
                expected_return_date=past_date,
                book=self.book,
                user=self.user,
            )

    def test_borrow_date_validation(self):
        future_date = self.borrow_date + timedelta(days=3)
        with self.assertRaises(ValidationError):
            Borrowing.objects.create(
                borrow_date=future_date,
                expected_return_date=self.expected_return_date,
                book=self.book,
                user=self.user,
            )

    def test_actual_return_date_validation(self):
        future_date = self.borrow_date + timedelta(days=3)
        with self.assertRaises(ValidationError):
            Borrowing.objects.create(
                borrow_date=self.borrow_date,
                expected_return_date=self.expected_return_date,
                actual_return_date=future_date,
                book=self.book,
                user=self.user,
            )
