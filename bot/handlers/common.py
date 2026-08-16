from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.keyboards.inline import get_spotify_auth_keyboard
from database.db_connection import User, async_session
from services.spotify_client import SpotifyAuthError, SpotifyClient, SpotifyClientError

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    telegram_id = message.from_user.id

    async with async_session() as session:
        user = await session.get(User, telegram_id)
        user_exists = user is not None and user.refresh_token is not None

    if user_exists:
        await message.answer(
            f"Привет, {message.from_user.full_name}! Рад видеть тебя в DJ-Spot.\n"
            "Используй /help, чтобы узнать бота лучше."
        )
    else:
        await message.answer(
            f"Привет, {message.from_user.full_name}! Добро пожаловать в DJ-Spot.\n\n"
            "Для работы с ботом необходимо привязать свой аккаунт Spotify. "
            "Нажми на кнопку ниже, чтобы пройти авторизацию:",
            reply_markup=get_spotify_auth_keyboard(message.from_user.id),
        )


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    telegram_id = message.from_user.id

    spotify = SpotifyClient(telegram_id=telegram_id)

    try:
        profile = await spotify.get_profile()

        display_name = profile.get("display_name", "Не указано")
        followers = profile.get("followers", {}).get("total", 0)
        country = profile.get("country", "Неизвестно")
        email = profile.get("email", "Скрыт")
        product = profile.get("product", "free").upper()

        profile_text = (
            "👤 **Ваш профиль Spotify:**\n\n"
            f"• **Имя:** {display_name}\n"
            f"• **Подписчики:** {followers}\n"
            f"• **Страна:** {country}\n"
            f"• **Email:** {email}\n"
            f"• **Подписка:** {product} ✨"
        )
        await message.answer(profile_text, parse_mode="Markdown")

    except SpotifyAuthError:
        await message.answer("❌ Вы не авторизованы или сессия истекла. Используйте /start для привязки аккаунта.")
    except SpotifyClientError as e:
        await message.answer(f"❌ Не удалось загрузить профиль: {e}")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📚 **Доступные команды:**\n\n"
        "/start - Начать работу / Авторизация\n"
        "/profile - Посмотреть свой профиль\n"
        "/search - Поиск треков и артистов\n"
        "/help - Справка",
        parse_mode="Markdown",
    )
