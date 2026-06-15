import asyncio
from aiogram import Bot, Dispatcher
from settings_bot import settings_router
from handlers import main_router

BOT_TOKEN = "5676600520:AAGz6EU7z2dESvhrZG6Rq59VpPwMklIQmyM"

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Routerlarni dispetcherga biriktirish
    dp.include_router(settings_router)
    dp.include_router(main_router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())