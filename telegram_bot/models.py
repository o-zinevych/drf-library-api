from django.conf import settings
from django.db import models


class TelegramProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"Chat ID: {self.chat_id}, user: {self.user.email}"
