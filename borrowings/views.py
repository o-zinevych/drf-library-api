from django.db.models import Q
from rest_framework import viewsets, mixins

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
)


class BorrowingViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingCreateSerializer

    def get_queryset(self):
        """Filter the queryset by user_id and activity status."""
        queryset = Borrowing.objects.select_related("book", "user")

        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if user_id:
            user_id = int(user_id)
            queryset = queryset.filter(user_id=user_id)
        if is_active == "true":
            queryset = queryset.filter(Q(actual_return_date__isnull=True))
        if is_active == "false":
            queryset = queryset.filter(Q(actual_return_date__isnull=False))

        return queryset
