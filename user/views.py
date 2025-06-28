from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from user.serializers import UserSerializer, UserAdminUpdateSerializer


class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """View to let authenticated users manage their own account."""

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
