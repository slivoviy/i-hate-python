from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Основная клавиатура
MAIN = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Последние новости")
).row(
    KeyboardButton("Новости по ключевому слову")
).row(
    KeyboardButton("Настроить рассылку новостей")
)

# Клавиатура с кнопками Да/Нет
YES_NO = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Да"),
    KeyboardButton("Нет")
)

# Клавиатура для настроек рассылки
SUB_SETTINGS = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Период рассылки новостей")
).add(
    KeyboardButton("Количество присылаемых новостей")
)

# Клавиатура для настроек времени рассылки
TIME_SETTINGS = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("24 часа"),
).add(
    KeyboardButton("12 часов"),
).row(
    KeyboardButton("6 часов"),
    KeyboardButton("2 часа"),
).row(
    KeyboardButton("1 час")
)
