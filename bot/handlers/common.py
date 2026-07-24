from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Привет, {message.from_user.full_name}! Добро пожаловать в DJ-Spot")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(f"Скоро...")