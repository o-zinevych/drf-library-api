import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

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
