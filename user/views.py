from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from user.serializers import UserSerializer


class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
