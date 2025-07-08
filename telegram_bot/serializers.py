from rest_framework import serializers

from telegram_bot.models import TelegramProfile


class TelegramProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = TelegramProfile
        fields = ("id", "email", "chat_id")
