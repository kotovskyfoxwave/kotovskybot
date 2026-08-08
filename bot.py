import os
import re

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["TOKEN"]
STICKER_ID = os.environ["STICKER_ID"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

# Список чатов, в которых бот уже видел сообщения
chat_ids = set()


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message:
        return

    # Запоминаем чат
    chat_ids.add(update.message.chat_id)

    # Если это не текст — ничего не делаем
    if not update.message.text:
        return

    text = update.message.text

    # Реагируем на:
    # да
    # daa
    # дааа
    # даааа
    # дааааа
    # даааааа
    if re.search(r"(?<!\w)да{1,6}(?!\w)", text, re.IGNORECASE):
        await update.message.reply_sticker(STICKER_ID)


async def broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    # Только администратор может использовать рассылку
    if not update.effective_user:
        return

    if update.effective_user.id != ADMIN_ID:
        return

    # Команда должна быть отправлена в личке боту
    if update.effective_chat.type != "private":
        await update.message.reply_text(
            "Рассылку нужно запускать в личке со мной."
        )
        return

    # Получаем текст после /broadcast
    if not context.args:
        await update.message.reply_text(
            "Использование:\n/broadcast Ваш текст"
        )
        return

    message = " ".join(context.args)

    sent = 0
    failed = 0

    for chat_id in list(chat_ids):
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=message
            )
            sent += 1
        except Exception as e:
            print(f"Не удалось отправить сообщение в {chat_id}: {e}")
            failed += 1

    await update.message.reply_text(
        f"Рассылка завершена.\n"
        f"Отправлено: {sent}\n"
        f"Ошибок: {failed}"
    )


app = Application.builder().token(TOKEN).build()

# Обычные сообщения
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)

# Команда рассылки
app.add_handler(
    CommandHandler("broadcast", broadcast)
)

app.run_polling()
