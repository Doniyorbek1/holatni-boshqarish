import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Update

class SystemLoggingMiddleware(BaseMiddleware):
    """
    Barcha kiruvchi Telegram so'rovlarini ushlab qoluvchi va 
    identifikatsiya ma'lumotlarini jurnallashtiruvchi markaziy middleware.
    """
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        
        user = data.get("event_from_user")
        if user:
            log_msg = f"So'rov qabul qilindi | UserID: {user.id} | Username: {user.username or 'Mavjud emas'}"
            
            # Xabar yoki tugma bosilishi (Callback) matnini ajratib olish
            if event.message and event.message.text:
                log_msg += f" | Harakat: XABAR | Matn: {event.message.text}"
            elif event.callback_query and event.callback_query.data:
                log_msg += f" | Harakat: CALLBACK | Ma'lumot: {event.callback_query.data}"
            else:
                log_msg += f" | Harakat: {event.event_type.upper()}"
                
            logging.info(log_msg)
            
        # Jarayonni keyingi handlerga o'tkazish
        return await handler(event, data)