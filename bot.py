import os
import re

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["TOKEN"]


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message:
        return

    # Если пришёл стикер — выводим его ID в логи Railway
    if update.message.sticker:
        sticker_id = update.message.sticker.file_id
        print(f"STICKER_ID = {sticker_id}")
        return

    # Если пришёл текст — проверяем слово "да"
    if not update.message.text:
        return

    text = update.message.text

    if re.search(r"(?<!\w)да(?!\w)", text, re.IGNORECASE):
        print('Получено слово "да", но STICKER_ID пока не настроен.')


app = Application.builder().token(TOKEN).build()

app.add_handler(
    MessageHandler(
        filters.ALL & ~filters.COMMAND,
        handle_message
    )
)

app.run_polling()
