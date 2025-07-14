from django.db import transaction
from rest_framework import serializers
from rest_framework.relations import StringRelatedField

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.SlugRelatedField(read_only=True, slug_field="title")

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "is_active",
            "book",
            "user_id",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user_id",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs)
        Borrowing.validate_book_inventory_is_not_zero(
            attrs["book"], serializers.ValidationError
        )
        Borrowing.validate_today_or_past_date(
            attrs["borrow_date"], "borrow_date", serializers.ValidationError
        )
        Borrowing.validate_future_date(
            attrs["expected_return_date"],
            "expected_return_date",
            serializers.ValidationError,
        )
        return data

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )

    @transaction.atomic
    def create(self, validated_data):
        borrowing = Borrowing.objects.create(**validated_data)
        book = borrowing.book
        book.inventory -= 1
        book.save()
        return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(BorrowingReturnSerializer, self).validate(attrs)
        Borrowing.validate_today_or_past_date(
            attrs["actual_return_date"],
            "actual_return_date",
            serializers.ValidationError,
        )
        return data

    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")

    @transaction.atomic
    def update(self, instance, validated_data):
        borrowing = super().update(instance, validated_data)
        book = borrowing.book
        book.inventory += 1
        book.save()
        return borrowing
