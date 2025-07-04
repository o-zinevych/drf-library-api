from django.urls import path

from telegram_bot.views import TelegramProfileRegisterView

urlpatterns = [
    path("register/", TelegramProfileRegisterView.as_view(), name="register"),
]

app_name = "telegram_bot"
