from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from user.serializers import UserSerializer, UserAdminUpdateSerializer


class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (IsAuthenticated(),)
        return (IsAdminUser(),)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return UserSerializer
        return UserAdminUpdateSerializer
