from django.db.models import Q
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

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
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Filter the queryset by current user's borrowings, activity status and user_id for admin."""
        queryset = Borrowing.objects.select_related("book", "user")

        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if self.request.user and self.request.user.is_superuser and user_id:
            user_id = int(user_id)
            queryset = queryset.filter(user_id=user_id)

        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)

        if is_active == "true":
            queryset = queryset.filter(Q(actual_return_date__isnull=True))
        if is_active == "false":
            queryset = queryset.filter(Q(actual_return_date__isnull=False))

        return queryset
