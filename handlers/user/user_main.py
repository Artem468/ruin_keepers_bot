import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select

from loader import *
from tables import ScheduledTours
from utils.user_input import Input

router = Router()


@router.message(Command('start'))
async def start(message: Message):
    await bot.send_message(
        chat_id=message.chat.id,
        text="<b>Бот запущен и готов помочь вам записаться на тур 🙃</b>",
        reply_markup=USER_KEYBOARD
    )


@router.message(F.text == UserButtons.create_entry.value)
async def create_entry(message: Message, state: FSMContext):
    async with (async_session() as session):
        scheduled_tours = (await session.execute(
            select(ScheduledTours).where(ScheduledTours.start_at >= datetime.datetime.now())
        )).scalars().all()
        await bot.send_message(
            chat_id=message.chat.id,
            text="Выберите тур",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="", callback_data="")] for item in scheduled_tours
                ]
            )
        )


    # name_message = await Input(
    #     chat_id=message.chat.id,
    #     text="<b>Введите как мы можем к вам обращаться:</b>",
    #     state=state
    # ).reply_markup(
    #     InlineKeyboardMarkup(
    #         inline_keyboard=[
    #             [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
    #         ]
    #     )
    # ).hide_keyboard_after().send_message()

