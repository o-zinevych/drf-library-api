import logging
import os

import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

EMAIL = 1
BACKEND_URL = os.getenv("BACKEND_URL")
TELEGRAM_ENDPOINT = f"{BACKEND_URL}/api/telegram-bot/register/"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text="Welcome to our library notification bot. Track your borrowings with ease!"
        "\nPlease, enter your email to start.",
    )
    return EMAIL


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    chat_id = update.effective_chat.id

    response = requests.post(
        TELEGRAM_ENDPOINT, json={"email": email, "chat_id": chat_id}
    )
    if response.status_code == 200:
        await update.message.reply_text("Your account has been linked!")
    else:
        await update.message.reply_text(
            "Failed to link your account. Check your email address and try again."
        )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


if __name__ == "__main__":
    application = ApplicationBuilder().token(os.getenv("TG_BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    application.run_polling()
