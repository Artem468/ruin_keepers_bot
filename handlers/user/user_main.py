import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from loader import *
from tables import ScheduledTours, Tour, Entries, Users
from utils.user_input import Input, call_input, Output

router = Router()


@router.message(Command('start'))
async def start(message: Message):
    await bot.send_message(
        chat_id=message.chat.id,
        text="<b>Бот запущен и готов помочь вам записаться на тур 🙃</b>",
        reply_markup=USER_KEYBOARD
    )
    async with (async_session() as session):
        user = Users(
            id=message.chat.id,
        )
        session.add(user)
        await session.commit()


@router.message(F.text == UserButtons.create_entry.value)
async def create_entry(message: Message):
    async with (async_session() as session):
        scheduled_tours: list[tuple[Tour, ScheduledTours]] = (await session.execute(
            select(Tour, ScheduledTours)
            .join(ScheduledTours, Tour.id == ScheduledTours.tour_id)
            .where(ScheduledTours.start_at >= datetime.datetime.now())
        )).all()
        await bot.send_message(
            chat_id=message.chat.id,
            text="Выберите тур",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{item[0].name} | {item[1].start_at.strftime("%d.%m %H:%M")} - {item[1].end_at.strftime("%d.%m %H:%M")}",
                            callback_data=f"tourName|{item[0].id}"
                        )
                    ] for item in scheduled_tours
                ]
            )
        )


@router.callback_query(F.data.startswith("tourName"))
async def select_tour(call: CallbackQuery, state: FSMContext):
    _, tour_id = call.data.split("|")

    await bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[]])
    )

    _keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
        ]
    )

    _keyboard_with_skip = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить", callback_data="skipField")],
            [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
        ]
    )

    _keyboard_count_members = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Только я", callback_data="skipField")],
            [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
        ]
    )

    name_message = await Input(
        chat_id=call.message.chat.id,
        text="<b>Напишите как мы можем к вам обращаться:</b>",
        state=state
    ).reply_markup(_keyboard).hide_keyboard_after().edit(message_id=call.message.message_id)

    email_message = await Input(
        chat_id=call.message.chat.id,
        text="<b>Введите вашу электронную почту или нажмите пропустить если ее нет:</b>",
        state=state
    ).reply_markup(_keyboard_with_skip).hide_keyboard_after().send_message()

    async def _get_phone():
        _res = await (
            Input(
                chat_id=call.message.chat.id,
                text="<b>Введите ваш контактный номер телефона:</b>",
                state=state)
            .reply_markup(_keyboard)
            .hide_keyboard_after()
            .send_message()
        )
        if not _res.message.text.isdigit():
            return await _get_phone()
        return _res

    phone_message = await _get_phone()

    count_members_message = await Input(
        chat_id=call.message.chat.id,
        text="<b>Сколько человек поедут с вами?</b>",
        state=state
    ).reply_markup(_keyboard_count_members).hide_keyboard_after().send_message()

    await state.update_data(
        tour_id=int(tour_id),
        name=name_message.to_return.text,
        email=email_message.to_return.text if email_message.to_return is not None else None,
        phone=phone_message.to_return.text,
        count_members=int(count_members_message.to_return.text) if count_members_message.to_return is not None else 0,
    )

    is_need_notify = await state.get_value("is_need_notify")
    is_need_lunch = await state.get_value("is_need_lunch")

    await bot.send_message(
        chat_id=call.message.chat.id,
        text="Нажмите на кнопку если вам это надо",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{"✅" if is_need_notify else ""} Напомните про тур",
                        callback_data="iWantNotify"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=f"{"✅" if is_need_lunch else ""} Нужен обед",
                        callback_data="iNeedLunch"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=f"Записаться",
                        callback_data="finishEntry"
                    )
                ]
            ]
        )
    )


@router.callback_query(F.data == "skipField")
@call_input
async def skip_field(call: CallbackQuery, **kwargs):
    return Output(
        message=call.message,
        to_return=None,
        bot_msg=call.message
    )


@router.callback_query(F.data == "iWantNotify")
async def want_notify(call: CallbackQuery, state: FSMContext):
    is_need_notify = not await state.get_value("is_need_notify")
    is_need_lunch = await state.get_value("is_need_lunch")
    await state.update_data(is_need_notify=is_need_notify)
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Нажмите на кнопку если вам это надо",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{"✅" if is_need_notify else ""} Напомните про тур",
                        callback_data="iWantNotify"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=f"{"✅" if is_need_lunch else ""} Нужен обед",
                        callback_data="iNeedLunch"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=f"Записаться",
                        callback_data="finishEntry"
                    )
                ]
            ]
        )
    )


@router.callback_query(F.data == "iNeedLunch")
async def need_lunch(call: CallbackQuery, state: FSMContext):
    is_need_lunch = not await state.get_value("is_need_lunch")
    is_need_notify = await state.get_value("is_need_notify")
    await state.update_data(is_need_lunch=is_need_lunch)
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Нажмите на кнопку если вам это надо",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{"✅" if is_need_notify else ""} Напомните про тур",
                        callback_data="iWantNotify"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=f"{"✅" if is_need_lunch else ""} Нужен обед",
                        callback_data="iNeedLunch"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=f"Записаться",
                        callback_data="finishEntry"
                    )
                ]
            ]
        )
    )


@router.callback_query(F.data == "finishEntry")
async def finish_entry(call: CallbackQuery, state: FSMContext):
    tour_id = await state.get_value("tour_id")
    name = await state.get_value("name")
    email = await state.get_value("email")
    phone = await state.get_value("phone")
    count_members = await state.get_value("count_members")
    is_need_notify = not not await state.get_value("is_need_notify")
    is_need_lunch = not not await state.get_value("is_need_lunch")

    await bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[]])
    )

    async with (async_session() as session):
        entry = Entries(
            scheduled_tour_id=tour_id,
            telegram_id=call.message.chat.id,
            name=name,
            email=email,
            phone=phone,
            is_need_lunch=is_need_lunch,
            is_need_notify=is_need_notify,
            count_members=count_members + 1
        )
        session.add(entry)
        await session.commit()
    await bot.send_message(
        chat_id=call.message.chat.id,
        text=f"<b>Вы записаны на тур 🤗</b>\n\n"
             f"{"<i>Мы напомним вам про тур ✨</i>\n" if is_need_notify else ""}"
             f"{"<i>Мы приготовим вам прекрасный обед 😋🍽️</i>" if is_need_lunch else ""}"
    )

    async with(async_session() as session):
        tour_entry = (
            await session.execute(select(Entries, ScheduledTours, Tour)
                                  .join(ScheduledTours, ScheduledTours.id == Entries.scheduled_tour_id)
                                  .join(Tour, Tour.id == ScheduledTours.tour_id)
                                  .where(Entries.id == tour_id)
                                  )).one_or_none()

        _entry, _scheduled_tour, _tour = tour_entry
        await bot.send_message(
            chat_id=MANAGER_CHAT,
            text=f"<b>Новая запись</b>\n\n"
                 f"<b>Тур:</b> {_tour.name}\n"
                 f"<b>Начало - конец:</b> {_scheduled_tour.start_at.strftime("%d.%m %H:%M")} - {_scheduled_tour.end_at.strftime("%d.%m %H:%M")}\n\n"
                 f"<b>Имя:</b> {_entry.name}\n"
                 f"<b>Email:</b> {_entry.email if _entry.email is not None else "---"}\n"
                 f"<b>Телефон:</b> {_entry.phone if _entry.phone is not None else "---"}\n"
                 f"<b>Обед:</b> {"Нужен" if _entry.is_need_lunch else "Не требуется"}\n"
                 f"<b>Количество человек:</b> {_entry.count_members}"
        )

