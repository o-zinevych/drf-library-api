from rest_framework import viewsets, mixins

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer


class BorrowingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingListSerializer
