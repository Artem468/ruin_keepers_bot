from aiogram import Router
from aiogram.filters import Command

from loader import *
from utils.user_input import *

router = Router()


@router.message(Command('admin'), flags={"is_admin": True})
async def admin_panel(message: Message, state: FSMContext, **kwargs):
    await bot.send_message(
        chat_id=message.chat.id,
        text="<b>Админ панель открыта</b>",
        reply_markup=ADMIN_KEYBOARD
    )
