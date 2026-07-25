import asyncio
import logging
import colorlog
from config import BOT_TOKEN
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BotCommand

from bot.handlers.common import router as common_routers
# from bot.handlers.music import router as music_router

def setup_logging():
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red',
        }
    ))

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command="start", description="🚀 Запустить бота / Главное меню"),
        BotCommand(command="search", description="🎵 Найти песню в Spotify"),
        BotCommand(command="help", description="❓ Помощь и управление"),
        BotCommand(command="profile", description="👤 Профиль Spotify"),
    ]
    await bot.set_my_commands(main_menu_commands)
    logging.info("Меню команд успешно загружено в Telegram!")


async def main():
    setup_logging()
    logging.info("Инилизация бота DJ-Spot...")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(common_routers)

    await set_main_menu(bot)

    logging.info("Бот DJ-Spot успешно запущен и готов к работе!")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
