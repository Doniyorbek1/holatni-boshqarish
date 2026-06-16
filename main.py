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
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # 2. Oraliq dasturni (Middleware) ro'yxatdan o'tkazish
    # Bu barcha marshrutlardan oldin ishga tushadi
    dp.update.outer_middleware(SystemLoggingMiddleware())
    
    # 3. Routerlarni biriktirish
    dp.include_router(settings_router)
    dp.include_router(main_router)
    
    logger.info("Tizim jarayonlari initsializatsiya qilindi. So'rovlar kutilmoqda (Polling amalda)...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
