from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
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
        if self.action == "return_borrowing":
            return BorrowingReturnSerializer
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="Filter borrowings list by user_id if admin.",
            ),
            OpenApiParameter(
                name="is_active", description="Filter borrowings list by their status."
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Return a borrowed book with automatic inventory update."
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
    )
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        if borrowing.actual_return_date:
            return Response(
                {"detail": "You've already returned this book."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(borrowing, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
