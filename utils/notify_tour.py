import datetime

from sqlalchemy import select

from loader import async_session, bot
from tables import Entries, ScheduledTours


async def notify_tour():
    now = datetime.datetime.now()
    limit_time = now + datetime.timedelta(hours=24)

    async with (async_session() as session):
        data = (
            await session.execute(
                select(Entries.telegram_id, ScheduledTours.start_at)
                .join(ScheduledTours, Entries.scheduled_tour_id == ScheduledTours.id)
                .where(
                    Entries.is_need_notify.is_(True),
                    Entries.telegram_id.isnot(None),
                    ScheduledTours.start_at <= limit_time,
                    ScheduledTours.start_at >= now
                ))
        ).all()
        for item in data:
            await bot.send_message(
                chat_id=item[0],
                text=f"<b>Здравствуйте, напоминаем вам что {item[1].strftime("%d.%m")} в "
                     f"{item[1].strftime("%H:%M")} у вас запланирован тур 😇</b>"
            )
