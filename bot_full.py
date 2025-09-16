import os
import asyncio
import requests
import tempfile
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from gtts import gTTS

# 🔑 Загружаем токены
TELEGRAM_TOKEN = os.getenv("8269598789:AAFrhPCLji4-CwJlV0E4pDI8XBNrCeVxrE4")
DEEPAI_API_KEY = os.getenv("3fe99229-4244-4ef6-92f5-7a6d4f66d8a0")

# Функция общения с DeepAI
def deepai_chat(prompt: str) -> str:
    url = "https://api.deepai.org/api/text-generator"
    headers = {"api-key": DEEPAI_API_KEY}
    response = requests.post(url, headers=headers, data={"text": prompt})
    data = response.json()
    return data.get("output", "⚠️ Ошибка при обращении к ИИ")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет, я Crazy Mita 🤖!\n"
        "Напиши мне текст или /voice [текст], и я отвечу как ИИ с голосом."
    )

# /voice — текст → ИИ → голос
async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /voice [текст]")
        return
    text = " ".join(context.args)

    reply = deepai_chat(text)

    # Озвучка через gTTS
    tts = gTTS(text=reply, lang="ru")
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        filename = f"{fp.name}.mp3"
        tts.save(filename)
        await update.message.reply_voice(voice=open(filename, "rb"), caption=reply)

# Просто текст → ответ ИИ
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    reply = deepai_chat(user_text)
    await update.message.reply_text(reply)

def main():
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN не найден в переменных окружения")
        return
    if not DEEPAI_API_KEY:
        print("❌ DEEPAI_API_KEY не найден в переменных окружения")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("voice", voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("✅ Crazy Mita запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
