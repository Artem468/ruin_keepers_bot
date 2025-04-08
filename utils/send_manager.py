import json

from aiohttp import web
from sqlalchemy import select

from loader import async_session, bot, MANAGER_CHAT
from tables import Entries, ScheduledTours, Tour


async def send_manager(request: web.Request):
    try:
        data = await request.json()
    except json.decoder.JSONDecodeError:
        return

    if data.get("tour") is None:
        return web.json_response({
            "status": "error",
            "message": "В запросе не указан ID тура"
        })

    async with (async_session() as session):
        tour_entry = (
            await session.execute(select(Entries, ScheduledTours, Tour)
                                  .join(ScheduledTours, ScheduledTours.id == Entries.scheduled_tour_id)
                                  .join(Tour, Tour.id == ScheduledTours.tour_id)
                                  .where(Entries.id == data.get("tour"))
                                  )).one_or_none()

        if tour_entry is None:
            return web.json_response({
                "status": "error",
                "message": "Такой ID тура не существует"
            })
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
        return web.json_response({
            "status": "ok"
        })
