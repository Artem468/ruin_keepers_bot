import datetime

from aiogram import types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from colorama import Fore, Style

from handlers import user, admin, core
from loader import *
from tables import init_models
from utils.notify_tour import notify_tour
from utils.send_manager import send_manager


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


async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)


async def on_shutdown(*_args, **_kwargs):
    print(f"{Style.BRIGHT}{Fore.RED}Бот отключен! "
          f"({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})",
          Style.RESET_ALL)
    await bot.session.close()


async def main(*args, **kwargs):
    try:
        from handlers import dp
        await bot.set_webhook(url=f"{WEBHOOK_URL}{WEBHOOK_BOT_PATH}")
        await on_startup()
        from utils.is_status import AdminMiddleware
        dp.message.middleware(AdminMiddleware())
        dp.callback_query.middleware(AdminMiddleware())

        dp.include_routers(
            user.user_main.router,

            admin.admin_main.router,

            core.core.router,
        )

    finally:
        ...


if __name__ == '__main__':
    app.on_startup.append(main)
    app.on_shutdown.append(on_shutdown)
    app.add_routes([
        web.post('/api/v1/sendManager', send_manager)
    ])

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    webhook_requests_handler.register(app, path=WEBHOOK_BOT_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host="127.0.0.1", port=8080)
