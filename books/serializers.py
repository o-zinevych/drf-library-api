from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from books.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")
        validators = [
            UniqueTogetherValidator(
                queryset=Book.objects.all(),
                fields=["title", "author"],
                message="This book already exists.",
            )
        ]

    def to_representation(self, instance):
        """Display cover as human-readable str instead of db value"""

        representation = super().to_representation(instance)
        representation["cover"] = instance.get_cover_display()
        return representation


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author")
