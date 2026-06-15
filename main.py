import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Bot tokenini ushbu o'zgaruvchiga kiriting
BOT_TOKEN = "SIZNING_BOT_TOKENINGIZ_SHU_YERDA"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Klaviatura arxitekturasi
mood_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="A'lo 🚀"), KeyboardButton(text="O'rtacha 📊")],
        [KeyboardButton(text="Yomon 📉"), KeyboardButton(text="Charchagan 🔋")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Holatingizni tanlang..."
)

# Ma'lumotlar va reaksiyalar matritsasi
MOOD_DATA = {
    "A'lo 🚀": {
        "sticker_id": "CAACAgIAAxkBAAE... (Stiker file_id kiritiladi)", 
        "advice": "Tahlil: Yuqori energiya holati. Diqqatni jamlash talab etiladigan analitik va mantiqiy jarayonlar uchun optimal vaqt.",
        "task": "Tavsiya: Kiberxavfsizlik amaliyotlari (masalan, TryHackMe platformasida ishlash), xavfsizlik protokollarini tahlil qilish yoki tarmoq shlyuzida yangi qurilmalar konfiguratsiyasini amalga oshirish."
    },
    "O'rtacha 📊": {
        "sticker_id": "CAACAgIAAxkBAAE... (Stiker file_id kiritiladi)",
        "advice": "Tahlil: Barqaror holat. Standart, uzluksiz va avtomatlashtirilgan jarayonlarni nazorat qilish uchun mos.",
        "task": "Tavsiya: Tizim jurnallarini (log files) tekshirish, SNMP monitoring tizimi orqali tarmoq qurilmalari holatini nazorat qilish yoki joriy texnik hujjatlarni yangilash."
    },
    "Yomon 📉": {
        "sticker_id": "CAACAgIAAxkBAAE... (Stiker file_id kiritiladi)",
        "advice": "Tahlil: Kognitiv resurslar pasaygan. Ruhiy zo'riqishni kamaytirish va muammolarni hal qilishdan chekinish zarur.",
        "task": "Tavsiya: Asosiy e'tiborni engilroq mashg'ulotlarga qarating. Axborot texnologiyalari tarixiga oid nazariy materiallarni o'qish yoki rus/ingliz tillaridagi texnik atamalar lug'atini ko'rib chiqish."
    },
    "Charchagan 🔋": {
        "sticker_id": "CAACAgIAAxkBAAE... (Stiker file_id kiritiladi)",
        "advice": "Tahlil: Jismoniy yoki aqliy charchoq. Miya faoliyatini boshqa turdagi yuklamaga o'tkazish talab etiladi.",
        "task": "Tavsiya: Kichik fizik harakatlarni bajaring. Ish o'rnini tartibga solish, hujjatlarni arxivlash yoki qurilmalarning tashqi holatini (masalan, sarflovchi materiallar zaxirasini) vizual ko'zdan kechirish."
    }
}

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    """Start buyrug'i uchun ishlov beruvchi funksiya."""
    await message.answer(
        "Tizim faollashtirildi. Bugun kognitiv holatingiz va kayfiyatingiz qanday?",
        reply_markup=mood_keyboard
    )

@dp.message(F.text.in_(MOOD_DATA.keys()))
async def process_mood(message: types.Message) -> None:
    """Tanlangan kayfiyatga asoslangan javobni shakllantirish funksiyasi."""
    user_mood = message.text
    data = MOOD_DATA[user_mood]
    
    # Stiker yuborish (Izoh: haqiqiy file_id kiritilgunga qadar xato bermasligi uchun try-except blokida yoki matn bilan almashtirilgan)
    try:
         await message.answer_sticker(data["sticker_id"])
    except Exception:
         # Agar stiker ID noto'g'ri bo'lsa, o'rniga vizual belgi yuboriladi
         await message.answer("✨ [Stiker o'rni]")
         
    # Tahlil va tavsiyani yuborish
    response_text = f"{data['advice']}\n\n{data['task']}"
    await message.answer(response_text)

@dp.message()
async def unknown_input(message: types.Message) -> None:
    """Noma'lum kiritishlarga reaksion funksiya."""
    await message.answer("Surov xato. Iltimos, taqdim etilgan klaviatura tugmalaridan birini tanlang.", reply_markup=mood_keyboard)

async def main() -> None:
    """Asosiy asinxron siklni ishga tushirish."""
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())