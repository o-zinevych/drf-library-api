import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

EMAIL = 1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text="Welcome to our library notification bot. Track your borrowings with ease!"
        "\nPlease, enter your email to start.",
    )
    return EMAIL


if __name__ == "__main__":
    application = ApplicationBuilder().token(os.getenv("TG_BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
    )
    application.add_handler(conv_handler)

    application.run_polling()
