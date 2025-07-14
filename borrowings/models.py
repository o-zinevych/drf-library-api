import datetime

from django.conf import settings
from django.db import models
from rest_framework.exceptions import ValidationError

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        ordering = ["expected_return_date"]

    def __str__(self):
        return f"{self.book.title} due {self.expected_return_date}"

    @property
    def is_active(self):
        return not bool(self.actual_return_date)

    @staticmethod
    def validate_future_date(date, borrowing_date_attr, error_to_raise):
        """Validates expected return date."""
        if date <= datetime.date.today():
            raise error_to_raise(
                {borrowing_date_attr: f"This date must be in the future."}
            )

    @staticmethod
    def validate_today_or_past_date(date, borrowing_date_attr, error_to_raise):
        """Validates borrow and actual return dates."""
        if date and date > datetime.date.today():
            raise error_to_raise(
                {borrowing_date_attr: f"This date must be today or in the past."}
            )

    @staticmethod
    def validate_book_inventory_is_not_zero(book, error_to_raise):
        """Validates book inventory is available for borrowing."""
        if book.inventory == 0:
            raise error_to_raise(
                {"book_inventory": f"This book is unavailable for borrowing."}
            )

    def clean(self):
        self.validate_today_or_past_date(
            self.borrow_date, "borrow_date", ValidationError
        )

        self.validate_future_date(
            self.expected_return_date, "expected_return_date", ValidationError
        )
        self.validate_today_or_past_date(
            self.actual_return_date, "actual_return_date", ValidationError
        )
        self.validate_book_inventory_is_not_zero(self.book, ValidationError)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
