from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from telegram_bot.models import TelegramProfile
from telegram_bot.serializers import TelegramProfileSerializer

User = get_user_model()


class TelegramProfileRegisterView(APIView):
    serializer_class = TelegramProfileSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = TelegramProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        chat_id = serializer.validated_data["chat_id"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "This user doesn't exist"}, status=status.HTTP_404_NOT_FOUND
            )

        TelegramProfile.objects.update_or_create(
            user=user, defaults={"chat_id": chat_id}
        )
        return Response({"success": True}, status=status.HTTP_200_OK)
