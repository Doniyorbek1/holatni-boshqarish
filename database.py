import json
import os

JSON_FILE = "mood_data.json"

def load_all_data():
    """Barcha foydalanuvchilar ma'lumotlarini xotiraga yuklash."""
    if not os.path.exists(JSON_FILE) or os.path.getsize(JSON_FILE) == 0:
        return {}
    with open(JSON_FILE, 'r', encoding='utf-8') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def save_all_data(data):
    """Barcha ma'lumotlarni JSON faylga yozish."""
    with open(JSON_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def get_user_data(user_id: int) -> dict:
    """Aniq foydalanuvchi identifikatori bo'yicha ma'lumotlarni olish."""
    data = load_all_data()
    user_id_str = str(user_id)
    if user_id_str not in data:
        return {}
    return data[user_id_str]

def save_user_data(user_id: int, user_data: dict):
    """Aniq foydalanuvchi identifikatori bo'yicha ma'lumotlarni yangilash."""
    data = load_all_data()
    data[str(user_id)] = user_data
    save_all_data(data)