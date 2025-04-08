import traceback

from aiogram.types import InputMediaPhoto, URLInputFile
from aiohttp import web
from sqlalchemy import select

from loader import async_session, VK_SECRET, bot
from tables import Users


async def vk_hook(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        if data.get("secret") != VK_SECRET:
            raise Exception
        _obj = data.get("object")
        _photos = tuple(filter(lambda item: "photo" in item.keys(), _obj.get("attachments")))

        async with (async_session() as session):
            users = (await session.execute(select(Users.id))).scalars().all()
            if _photos:
                for user in users:
                    await bot.send_media_group(
                        chat_id=user,
                        media=[
                            InputMediaPhoto(
                                media=URLInputFile(img["photo"]["orig_photo"]["url"]),
                                caption=f"{_obj.get('text')}",
                            ) for img in _photos
                        ],
                    )
            else:
                for user in users:
                    await bot.send_message(
                        chat_id=user,
                        text=f"{_obj.get('text')}",
                    )
    except Exception:
        print(traceback.format_exc())

    finally:
        return web.Response(text='ok', content_type='plain/text')
