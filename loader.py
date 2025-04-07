import enum
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

ADMINS = [
    932288986
]

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(bot=bot, storage=MemoryStorage())

app = web.Application()

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_BOT_PATH = f"/botWebhooks/"

MANAGER_CHAT = os.getenv("MANAGER_CHAT")

POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_TABLENAME = os.getenv("POSTGRES_TABLENAME")

engine = create_async_engine(
    f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_TABLENAME}"
)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class AdminButtons(enum.Enum):
    mailing = "Рассылка"


ADMIN_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=item.value, callback_data=item.name)] for item in AdminButtons
    ]
)


class UserButtons(enum.Enum):
    create_entry = "Записать на тур"


USER_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=item.value)] for item in UserButtons
    ]
)
