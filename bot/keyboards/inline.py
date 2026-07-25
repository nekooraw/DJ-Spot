from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import url_spotify

kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🔑 Войти через Spotify", url=url_spotify)
    ]
])