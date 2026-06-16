import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from settings_bot import settings_router
from handlers import main_router
from middlewares import SystemLoggingMiddleware

# 1. .env faylidagi ma'lumotlarni OS xotirasiga yuklash
load_dotenv()

# 2. Muhit o'zgaruvchisidan tokenni qabul qilish
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 3. Validatsiya: Token mavjudligini tekshirish
if not BOT_TOKEN:
    raise ValueError("Kritik xatolik: BOT_TOKEN muhit o'zgaruvchisi topilmadi. .env faylini tekshiring.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("MainSystem")

# Qolgan funksiyalar (async def main()...) o'zgarishsiz qoladi