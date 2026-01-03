import os

from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


async def send_telegram_message(text: str):
    async with Bot(token=BOT_TOKEN) as bot:
        await bot.send_message(chat_id=CHAT_ID, text=text)


async def send_telegram_message_docx(docx_path: str, caption: str):
    async with Bot(token=BOT_TOKEN) as bot:
        with open(docx_path, "rb") as f:
            await bot.send_document(chat_id=CHAT_ID, document=f, caption=caption)
