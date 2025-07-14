from django.test import TestCase

from books.models import Book


class BookModelTests(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Hamlet",
            author="William Shakespeare",
            cover="SOFT",
            inventory=1,
            daily_fee=0.5,
        )

    def test_book_str(self):
        expected_str = f"{self.book.title} by {self.book.author}"
        self.assertEqual(expected_str, str(self.book))
