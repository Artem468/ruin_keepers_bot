from aiohttp import web


async def vk_hook(request: web.Request) -> web.Response:
    return web.Response(
        text='3353906d',
        content_type='text/html')