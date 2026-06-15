import asyncio
import logging
from aiogram import Bot, Dispatcher
from settings_bot import settings_router
from handlers import main_router
from middlewares import SystemLoggingMiddleware

BOT_TOKEN = "5676600520:AAGz6EU7z2dESvhrZG6Rq59VpPwMklIQmyM"

# 1. Jurnallashtirish (Logging) konfiguratsiyasi
logging.basicConfig(
    level=logging.INFO, # INFO va undan yuqori darajadagi loglarni chiqarish
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("MainSystem")

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