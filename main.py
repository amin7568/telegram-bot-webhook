import re
import asyncio
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus
import os

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

# ---------------------------
# خوش‌آمدگویی به اعضای جدید
# ---------------------------
@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=True))
async def welcome(event: ChatMemberUpdated):
    if event.new_chat_member.status == ChatMemberStatus.MEMBER:
        user = event.new_chat_member.user
        await bot.send_message(
            event.chat.id,
            f"سلام {user.full_name} 🌟\nخوش اومدی به گروه!"
        )

# ---------------------------
# حذف پیام‌های دارای لینک
# ---------------------------
LINK_REGEX = r"(https?://|t\.me/|telegram\.me/|www\.)"

@dp.message()
async def delete_links(message: types.Message):
    if message.text and re.search(LINK_REGEX, message.text):
        try:
            await message.delete()
        except:
            pass

# ---------------------------
# FastAPI Routes
# ---------------------------

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}

# ---------------------------
# Startup Event → Set Webhook
# ---------------------------
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

# ---------------------------
# Shutdown Event → Delete Webhook
# ---------------------------
@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
