import asyncio
import logging

import colorlog
import httpx
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from bot.handlers.common import router as common_routers
from bot.handlers.music import router as music_router
from config import BOT_TOKEN
from database.db_connection import init_db


def setup_logging():
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    )

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command="start", description="🚀 Запустить бота / Главное меню"),
        BotCommand(command="search", description="🎵 Найти песню в Spotify"),
        BotCommand(command="help", description="❓ Помощь и управление"),
        BotCommand(command="profile", description="👤 Профиль Spotify"),
    ]
    await bot.set_my_commands(main_menu_commands)


async def main():
    logger = setup_logging()
    logger.info("Инилизация бота DJ-Spot...")

    logger.info("Меню команд успешно загружено в Telegram!")

    await init_db()
    logger.info("База данных успешно инициализирована!")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    http_client = httpx.AsyncClient()
    dp["http_client"] = http_client

    dp.include_router(common_routers)
    dp.include_router(music_router)

    await set_main_menu(bot)

    logger.info("Бот DJ-Spot успешно запущен и готов к работе!")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await http_client.aclose()
        logger.info("Все сессии закрыты. Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
