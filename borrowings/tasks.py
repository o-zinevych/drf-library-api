import os

import requests
from celery import shared_task
from dotenv import load_dotenv

from borrowings.models import Borrowing
from telegram_bot.models import TelegramProfile

load_dotenv()

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")


def send_telegram_message(chat_id: str, text: str):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    return requests.post(url, json=payload)


@shared_task
def notify_user_about_borrowing(borrowing_id: int):
    try:
        borrowing = Borrowing.objects.select_related("user", "book").get(
            id=borrowing_id
        )
        telegram_profile = TelegramProfile.objects.get(user=borrowing.user)

        message = (
            f"📚New Borrowing Created!\n"
            f"Book: {borrowing.book.title}\n"
            f"Borrowed on: {borrowing.borrow_date}\n"
            f"Due: {borrowing.expected_return_date}\n"
        )

        send_telegram_message(telegram_profile.chat_id, message)
    except (Borrowing.DoesNotExist, TelegramProfile.DoesNotExist):
        pass
