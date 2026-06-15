from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_user_data, save_user_data

settings_router = Router()

# ================= FSM HOLATLARI =================
class SetupFSM(StatesGroup):
    waiting_for_name = State()
    waiting_for_mood_name = State()
    waiting_for_action_desc = State()
    waiting_for_action_url = State()

# ================= KLAIVIATURALAR =================
def settings_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Yangi kayfiyat qo'shish ➕", callback_data="set_add_mood")],
        [InlineKeyboardButton(text="Mavjud kayfiyatni tahrirlash ⚙️", callback_data="set_edit_mood")],
        [InlineKeyboardButton(text="Yakunlash ✅", callback_data="set_finish")]
    ])

def moods_list_kb(moods_dict):
    rows = []
    for mood in moods_dict.keys():
        rows.append([InlineKeyboardButton(text=f"{mood.capitalize()}", callback_data=f"edit_{mood}")])
    rows.append([InlineKeyboardButton(text="Ortga 🔙", callback_data="set_back_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ================= INITSIALIZATSIYA VA SETTINGS =================

@settings_router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    db = get_user_data(user_id)
    
    if "user_name" not in db:
        await state.set_state(SetupFSM.waiting_for_name)
        await message.answer("Tizimga xush kelibsiz. Initsializatsiya jarayonini boshlash uchun ismingizni kiriting:")
    else:
        await message.answer(
            f"Tizim faol, {db['user_name']}. \n\n"
            f"• Kundalik rejim uchun: /status buyrug'ini yuboring.\n"
            f"• Sozlamalar uchun: /settings buyrug'ini yuboring."
        )

@settings_router.message(SetupFSM.waiting_for_name)
async def process_name_init(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.text.strip()
    
    db = get_user_data(user_id)
    db["user_name"] = name
    db["moods"] = {}
    save_user_data(user_id, db)
    
    await state.clear()
    await message.answer(
        "Identifikatsiya muvaffaqiyatli yakunlandi. Asosiy sozlamalar paneliga o'tish uchun quyidagi menyudan foydalaning.",
        reply_markup=settings_main_kb()
    )

@settings_router.message(Command("settings"))
async def settings_command_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.clear()
    db = get_user_data(user_id)
    
    if "user_name" not in db:
        await message.answer("Dastlab /start buyrug'i orqali initsializatsiyadan o'ting.")
        return
    await message.answer("Konfiguratsiya paneli:", reply_markup=settings_main_kb())

# ================= YANGI KAYFIYAT QO'SHISH =================

@settings_router.callback_query(F.data == "set_add_mood")
async def add_mood_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(SetupFSM.waiting_for_mood_name)
    await callback.message.edit_text("Yangi kayfiyat nomini kiriting (masalan: Ijobiy, Stress, Diqqatli):")
    await callback.answer()

@settings_router.message(SetupFSM.waiting_for_mood_name)
async def process_new_mood_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    mood_name = message.text.strip().lower()
    
    db = get_user_data(user_id)
    if mood_name not in db.get("moods", {}):
        if "moods" not in db:
            db["moods"] = {}
        db["moods"][mood_name] = []
        save_user_data(user_id, db)
        
    await state.update_data(current_mood=mood_name)
    await state.set_state(SetupFSM.waiting_for_action_desc)
    await message.answer(
        f"'{mood_name.capitalize()}' holati yaratildi. Ushbu holatda qanday harakat bajarasiz?\n"
        f"Ta'rif kiriting (masalan: Youtube ko'rish, Kitob o'qish):"
    )

# ================= MA'LUMOT VA HAVOLA BIRIKTIRISH =================

@settings_router.callback_query(F.data == "set_edit_mood")
async def edit_mood_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    db = get_user_data(user_id)
    
    if not db.get("moods"):
        await callback.message.edit_text("Tahrirlash uchun holatlar mavjud emas. Dastlab yangi holat qo'shing.", reply_markup=settings_main_kb())
        return
    await callback.message.edit_text("Qaysi holatga yangi harakat biriktirmoqchisiz?", reply_markup=moods_list_kb(db["moods"]))
    await callback.answer()

@settings_router.callback_query(F.data.startswith("edit_"))
async def process_edit_mood_selection(callback: types.CallbackQuery, state: FSMContext):
    mood_name = callback.data.split("_")[1]
    await state.update_data(current_mood=mood_name)
    await state.set_state(SetupFSM.waiting_for_action_desc)
    await callback.message.edit_text(f"'{mood_name.capitalize()}' holati uchun yangi harakat ta'rifini kiriting:")
    await callback.answer()

@settings_router.message(SetupFSM.waiting_for_action_desc)
async def process_action_description(message: types.Message, state: FSMContext):
    desc = message.text.strip()
    await state.update_data(current_desc=desc)
    await state.set_state(SetupFSM.waiting_for_action_url)
    await message.answer("Ushbu harakat uchun URL manzilni (kanal, veb-sayt yoki resurs linki) kiriting:")

@settings_router.message(SetupFSM.waiting_for_action_url)
async def process_action_url(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    raw_url = message.text.strip()
    
    # ================= AVTOMATIK FORMATLASH =================
    if raw_url.startswith("@"):
        # Agar @Botfaz kiritilsa -> https://t.me/Botfaz
        url = f"https://t.me/{raw_url[1:]}"
    elif not raw_url.startswith(("http://", "https://")):
        # Agar shunchaki youtube.com kiritilsa -> https://youtube.com
        url = f"https://{raw_url}"
    else:
        # Agar manzil to'g'ri (https://...) kiritilgan bo'lsa, o'zgarishsiz qoladi
        url = raw_url
    # =========================================================

    user_data = await state.get_data()
    mood_name = user_data["current_mood"]
    desc = user_data["current_desc"]
    
    db = get_user_data(user_id)
    db["moods"][mood_name].append({"desc": desc, "url": url})
    save_user_data(user_id, db)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Yana harakat qo'shish ➕", callback_data=f"edit_{mood_name}")],
        [InlineKeyboardButton(text="Bosh menyu 🔙", callback_data="set_back_main")]
    ])
    
    # Foydalanuvchiga qanday saqlanganini ko'rsatish
    await message.answer(
        f"✅ Saqlandi!\n\n"
        f"📝 Harakat: {desc}\n"
        f"🔗 Havola: {url}\n\n"
        f"Keyingi amalni tanlang:", 
        reply_markup=kb,
        disable_web_page_preview=True
    )
# ================= NAVIGATSIYA =================

@settings_router.callback_query(F.data == "set_back_main")
async def back_to_main_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Konfiguratsiya paneli:", reply_markup=settings_main_kb())
    await callback.answer()

@settings_router.callback_query(F.data == "set_finish")
async def finish_settings_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Sozlamalar jarayoni yakunlandi. Operatsion rejimga o'tish uchun /status buyrug'ini yuboring.")
    await callback.answer()