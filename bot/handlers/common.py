from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from bot.keyboards.inline import kb, url_spotify

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    # Здесь в потом будет проверка в Базе Данных:
    # user_exists = назавниебд.db(message.from_user.id)
    user_exists = False # Пока заглушка как будто пользователя еще нет

    if user_exists:
        await message.answer(
            f"Привет, {message.from_user.full_name}! Рад видеть тебя в DJ-Spot.\n"
            "Используй /help чтобы узнать бота лучшее"
        )
    else:
        await message.answer(
            f"Привет, {message.from_user.full_name}! Добро пожаловать в DJ-Spot.\n\n"
            "Для работы с ботом необходимо привязать свой аккаунт Spotify. "
            "Нажми на кнопку ниже, чтобы пройти авторизацию:",
            reply_markup=kb
        )

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    #Все еще ждем бд все такое, замена на настояший
    profile_text = (
        "👤 **Ваш профиль Spotify:**\n\n"
        "• **Имя:** eco 1kd\n"
        "• **Подписчики:** 142 👥\n"
        "• **Страна:** RU\n"
        "• **Email:** user@example.com\n"
        "• **Подписка:** Premium ✨"
    )
    await message.answer(profile_text, parse_mode="Markdown")

@router.message(Command("search"))
async def cmd_search(message: Message):
    await message.answer("Скоро...")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📚 **Доступные команды:**\n\n"
        "/start - Начать работу / Авторизация\n"
        "/profile - Посмотреть свой профиль\n"
        "/search - Поиск треков и артистов\n"
        "/help - Справка"
    )