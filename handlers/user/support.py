from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from loader import *
from utils.user_input import Input, Output

router = Router()


@router.message(F.text == UserButtons.support.value)
async def support(message: Message, state: FSMContext):
    _keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
        ]
    )

    support_message: Output = await (
        Input(
            chat_id=message.chat.id,
            text="<b>Напишите свой вопрос и мы поможем вам разобраться 😉</b>",
            state=state)
        .reply_markup(_keyboard)
        .hide_keyboard_after()
        .send_message()
    )

    await bot.copy_message(
        chat_id=MANAGER_CHAT,
        from_chat_id=message.chat.id,
        message_id=support_message.message.message_id,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Ответить", callback_data=f"answerQuestion|{message.chat.id}")]
            ]
        )
    )


@router.callback_query(F.data.startswith("answerQuestion"))
async def answer_question(call: CallbackQuery, state: FSMContext):
    _, receiver_id = call.data.split("|")
    _keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
        ]
    )
    support_answer: Output = await (
        Input(
            chat_id=call.message.chat.id,
            text="<b>Напишите ответ:</b>",
            state=state)
        .reply_markup(_keyboard)
        .hide_keyboard_after()
        .send_message()
    )

    await bot.copy_message(
        chat_id=receiver_id,
        from_chat_id=call.message.chat.id,
        message_id=support_answer.message.message_id,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Ответить", callback_data=f"answerQuestion|{call.message.chat.id}")]
            ]
        )
    )