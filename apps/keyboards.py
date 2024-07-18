from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


russian_english_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Русская версия', callback_data="Russian_version")],
    [InlineKeyboardButton(text='English version', callback_data="English_version")],
])

change_lang = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Русская версия", callback_data="english_to_russian")],
    [InlineKeyboardButton(text='English version', callback_data="russian_to_english")],
    [InlineKeyboardButton(text='Cancle-отмена', callback_data="cancle")],

])