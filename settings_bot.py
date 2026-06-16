from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from database import get_user_data, save_user_data

settings_router = Router()

# ================= 1. FSM HOLATLARI =================
class SetupFSM(StatesGroup):
    waiting_for_name = State()
    waiting_for_mood_name = State()
    waiting_for_action_desc = State()
    waiting_for_action_url = State()

# ================= 2. KLAVIATURALAR VA INTERFEYS =================
def base_reply_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Status 🔄"), KeyboardButton(text="Sozlamalar ⚙️")]],
        resize_keyboard=True,
        input_field_placeholder="Harakatni tanlang..."
    )

def settings_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Yangi kayfiyat qo'shish ➕", callback_data="set_add_mood")],
        [InlineKeyboardButton(text="Kayfiyatni tahrirlash (Harakatlar) ⚙️", callback_data="set_edit_mood")],
        [InlineKeyboardButton(text="Kayfiyatni o'chirish 🗑", callback_data="set_del_mood")],
        [InlineKeyboardButton(text="Menyuni yopish 🏠", callback_data="set_finish")]
    ])

def moods_list_kb(moods_dict, prefix="edit"):
    rows = []
    for mood in moods_dict.keys():
        rows.append([InlineKeyboardButton(text=f"{mood.capitalize()}", callback_data=f"{prefix}_{mood}")])
    rows.append([InlineKeyboardButton(text="Ortga 🔙", callback_data="set_back_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def mood_actions_dashboard_kb(mood_name):
    """Kayfiyat ichki boshqaruv paneli klaviaturasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Yangi harakat qo'shish ➕", callback_data=f"addact_{mood_name}")],
        [InlineKeyboardButton(text="Harakatni o'chirish 🗑", callback_data=f"delactmenu_{mood_name}")],
        [InlineKeyboardButton(text="Ortga 🔙", callback_data="set_edit_mood")]
    ])

def delete_single_action_kb(mood_name, actions):
    """Alohida harakatlarni indeks bo'yicha o'chirish klaviaturasi."""
    rows = []
    for idx, action in enumerate(actions):
        # Telegram Callback Data limiti 64 bayt bo'lgani uchun, qisqartirilgan matn va indeks ishlatiladi
        btn_text = f"🗑 {action['desc'][:25]}..." if len(action['desc']) > 25 else f"🗑 {action['desc']}"
        rows.append([InlineKeyboardButton(text=btn_text, callback_data=f"delact_{mood_name}_{idx}")])
    rows.append([InlineKeyboardButton(text="Ortga 🔙", callback_data=f"edit_{mood_name}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ================= 3. INITSIALIZATSIYA VA ASOSIY MENYU =================
@settings_router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    db = get_user_data(user_id)
    if "user_name" not in db:
        await state.set_state(SetupFSM.waiting_for_name)
        await message.answer("Tizimga xush kelibsiz. Initsializatsiya uchun ismingizni kiriting:")
    else:
        await message.answer("Asosiy menyu faollashtirildi.", reply_markup=base_reply_kb())

@settings_router.message(SetupFSM.waiting_for_name)
async def process_name_init(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    db = get_user_data(user_id)
    db["user_name"] = message.text.strip()
    db["moods"] = {}
    save_user_data(user_id, db)
    await state.clear()
    await message.answer("Identifikatsiya yakunlandi.", reply_markup=base_reply_kb())

@settings_router.message(Command("settings"))
@settings_router.message(F.text == "Sozlamalar ⚙️")
async def settings_command_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.clear()
    if "user_name" not in get_user_data(user_id):
        await message.answer("Dastlab /start orqali initsializatsiyadan o'ting.")
        return
    await message.answer("Konfiguratsiya paneli:", reply_markup=settings_main_kb())

# ================= 4. KAYFIYAT DARAJASIDAGI OPERATSIYALAR =================
@settings_router.callback_query(F.data == "set_add_mood")
async def add_mood_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(SetupFSM.waiting_for_mood_name)
    await callback.message.edit_text(
        "Yangi kayfiyat nomini kiriting:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Ortga 🔙", callback_data="set_back_main")]])
    )
    await callback.answer()

@settings_router.message(SetupFSM.waiting_for_mood_name)
async def process_new_mood_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    mood_name = message.text.strip().lower()
    db = get_user_data(user_id)
    
    if mood_name not in db.get("moods", {}):
        if "moods" not in db: db["moods"] = {}
        db["moods"][mood_name] = []
        save_user_data(user_id, db)
        
    await state.update_data(current_mood=mood_name)
    await state.set_state(SetupFSM.waiting_for_action_desc)
    await message.answer(f"'{mood_name.capitalize()}' holati yaratildi. Ushbu holat uchun birinchi harakat ta'rifini kiriting:")

@settings_router.callback_query(F.data == "set_del_mood")
async def del_mood_callback(callback: types.CallbackQuery):
    db = get_user_data(callback.from_user.id)
    if not db.get("moods"):
        await callback.message.edit_text("O'chirish uchun holatlar mavjud emas.", reply_markup=settings_main_kb())
        return
    await callback.message.edit_text("Qaysi holatni bazadan o'chirib tashlamoqchisiz?", reply_markup=moods_list_kb(db["moods"], prefix="del"))
    await callback.answer()

@settings_router.callback_query(F.data.startswith("del_"))
async def process_del_mood_selection(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    mood_name = callback.data.split("_")[1]
    db = get_user_data(user_id)
    if mood_name in db.get("moods", {}):
        del db["moods"][mood_name]
        save_user_data(user_id, db)
    await callback.message.edit_text(f"'{mood_name.capitalize()}' holati to'liq o'chirildi.", reply_markup=settings_main_kb())
    await callback.answer()

# ================= 5. HARAKAT DARAJASIDAGI OPERATSIYALAR (YANGILANGAN) =================
@settings_router.callback_query(F.data == "set_edit_mood")
async def edit_mood_callback(callback: types.CallbackQuery):
    db = get_user_data(callback.from_user.id)
    if not db.get("moods"):
        await callback.message.edit_text("Tahrirlash uchun holatlar mavjud emas.", reply_markup=settings_main_kb())
        return
    await callback.message.edit_text("Boshqarish uchun holatni tanlang:", reply_markup=moods_list_kb(db["moods"], prefix="edit"))
    await callback.answer()

@settings_router.callback_query(F.data.startswith("edit_"))
async def view_mood_details(callback: types.CallbackQuery, state: FSMContext):
    """Kayfiyat ichidagi harakatlar ro'yxatini va boshqaruv panelini ko'rsatish."""
    await state.clear()
    user_id = callback.from_user.id
    mood_name = callback.data.split("_")[1]
    db = get_user_data(user_id)
    actions = db.get("moods", {}).get(mood_name, [])

    text = f"⚙️ Holat: **{mood_name.capitalize()}**\n\n📝 **Joriy biriktirilgan harakatlar ro'yxati:**\n"
    if not actions:
        text += "▫️ Ro'yxat bo'sh. Harakatlar kiritilmagan."
    else:
        for idx, act in enumerate(actions, 1):
            text += f"{idx}. {act['desc']}\n   🔗 {act['url']}\n\n"

    await callback.message.edit_text(text, reply_markup=mood_actions_dashboard_kb(mood_name), disable_web_page_preview=True)
    await callback.answer()

@settings_router.callback_query(F.data.startswith("addact_"))
async def trigger_add_action(callback: types.CallbackQuery, state: FSMContext):
    """Tanlangan kayfiyatga yangi harakat qo'shish jarayonini boshlash."""
    mood_name = callback.data.split("_")[1]
    await state.update_data(current_mood=mood_name)
    await state.set_state(SetupFSM.waiting_for_action_desc)
    await callback.message.edit_text(
        f"'{mood_name.capitalize()}' holati uchun yangi harakat ta'rifini kiriting:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Ortga 🔙", callback_data=f"edit_{mood_name}")]])
    )
    await callback.answer()

@settings_router.callback_query(F.data.startswith("delactmenu_"))
async def trigger_delete_action_menu(callback: types.CallbackQuery):
    """Aniq bir harakatni o'chirish uchun menyu taqdim etish."""
    mood_name = callback.data.split("_")[1]
    user_id = callback.from_user.id
    db = get_user_data(user_id)
    actions = db.get("moods", {}).get(mood_name, [])

    if not actions:
        await callback.answer("O'chirish uchun harakatlar mavjud emas.", show_alert=True)
        return

    await callback.message.edit_text(
        f"'{mood_name.capitalize()}' ro'yxatidan qaysi harakatni o'chirib tashlaysiz?",
        reply_markup=delete_single_action_kb(mood_name, actions)
    )
    await callback.answer()

@settings_router.callback_query(F.data.startswith("delact_"))
async def execute_action_deletion(callback: types.CallbackQuery):
    """Indeks bo'yicha harakatni xotiradan o'chirish."""
    parts = callback.data.split("_")
    mood_name = parts[1]
    index = int(parts[2])
    
    user_id = callback.from_user.id
    db = get_user_data(user_id)
    actions = db.get("moods", {}).get(mood_name, [])

    if 0 <= index < len(actions):
        deleted_act = actions.pop(index)
        save_user_data(user_id, db)
        await callback.answer(f"O'chirildi: {deleted_act['desc'][:20]}...", show_alert=False)
    else:
        await callback.answer("Sinxronizatsiya xatosi. Element topilmadi.", show_alert=True)

    # O'chirilgandan so'ng qayta yuklash (Refresh dashboard)
    await view_mood_details(callback, FSMContext(storage=None, key=None)) 

# ================= 6. MA'LUMOT VA HAVOLA QABUL QILISH =================
@settings_router.message(SetupFSM.waiting_for_action_desc)
async def process_action_description(message: types.Message, state: FSMContext):
    await state.update_data(current_desc=message.text.strip())
    await state.set_state(SetupFSM.waiting_for_action_url)
    await message.answer("Ushbu harakat uchun URL manzilni kiriting:")

@settings_router.message(SetupFSM.waiting_for_action_url)
async def process_action_url(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    raw_url = message.text.strip()
    
    if raw_url.startswith("@"): url = f"https://t.me/{raw_url[1:]}"
    elif not raw_url.startswith(("http://", "https://")): url = f"https://{raw_url}"
    else: url = raw_url

    user_data = await state.get_data()
    mood_name = user_data.get("current_mood")
    desc = user_data.get("current_desc")
    
    db = get_user_data(user_id)
    db["moods"][mood_name].append({"desc": desc, "url": url})
    save_user_data(user_id, db)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Yana harakat qo'shish ➕", callback_data=f"addact_{mood_name}")],
        [InlineKeyboardButton(text="Boshqaruv paneliga qaytish 🔙", callback_data=f"edit_{mood_name}")]
    ])
    await message.answer(f"✅ Saqlandi:\n📝 Harakat: {desc}\n🔗 Havola: {url}", reply_markup=kb, disable_web_page_preview=True)
    await state.clear()

# ================= 7. GLOBAL NAVIGATSIYA =================
@settings_router.callback_query(F.data == "set_back_main")
async def back_to_main_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Konfiguratsiya paneli:", reply_markup=settings_main_kb())
    await callback.answer()

@settings_router.callback_query(F.data == "set_finish")
async def finish_settings_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Konfiguratsiya yopildi. Operatsion rejim faol.", reply_markup=base_reply_kb())
    await callback.answer()