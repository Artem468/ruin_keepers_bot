from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from loader import *

router = Router()


@router.message(Command('start'), flags={"is_sub": True, "is_reg": True})
async def start(message: Message):
    await bot.send_message(
        chat_id=message.chat.id,
        text="<b>Started</b>"
    )