import asyncio
import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from colorama import Fore, Style

from handlers import user, admin, core
from loader import *
from tables import init_models
from utils.notify_tour import notify_tour


async def on_startup():
    await init_models()
    bot_info = await dp.get("bot").get_me()
    print(
        f"{Style.BRIGHT}{Fore.CYAN}https://t.me/{bot_info.username} запущен успешно! "
        f"({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})",
        Style.RESET_ALL
    )
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        func=notify_tour,
        trigger="cron",
        hour=16,
        timezone=datetime.timezone.utc
    )
    scheduler.start()


async def main():
    try:
        from handlers import dp
        await on_startup()
        from utils.is_status import AdminMiddleware
        dp.message.middleware(AdminMiddleware())
        dp.callback_query.middleware(AdminMiddleware())

        dp.include_routers(
            user.user_main.router,

            admin.admin_main.router,

            core.core.router,
        )

        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
