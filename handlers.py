from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_user_data

main_router = Router()

@main_router.message(Command("status"))
async def status_command_handler(message: types.Message):
    user_id = message.from_user.id
    db = get_user_data(user_id)
    
    if "user_name" not in db or not db.get("moods"):
        await message.answer("Tizim sozlanmagan. Iltimos, /settings buyrug'i orqali konfiguratsiyani amalga oshiring.")
        return
        
    rows = []
    current_row = []
    for mood in db["moods"].keys():
        current_row.append(InlineKeyboardButton(text=mood.capitalize(), callback_data=f"status_{mood}"))
        if len(current_row) == 2:
            rows.append(current_row)
            current_row = []
    if current_row:
        rows.append(current_row)
        
    await message.answer("Joriy kognitiv holatingizni tasdiqlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))

@main_router.callback_query(F.data.startswith("status_"))
async def execute_status_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    mood_name = callback.data.split("_")[1]
    
    db = get_user_data(user_id)
    actions = db.get("moods", {}).get(mood_name, [])
    
    if not actions:
        await callback.answer("Ushbu holat uchun resurslar biriktirilmagan.", show_alert=True)
        return
        
    action_buttons = []
    for action in actions:
        action_buttons.append([InlineKeyboardButton(text=action["desc"], url=action["url"])])
        
    await callback.message.edit_text(
        f"Holat: {mood_name.capitalize()}.\nTegishli resurslar:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=action_buttons)
    )
    await callback.answer()