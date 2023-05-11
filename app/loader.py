from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import JSONStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from app.utils.config import BOT_API_TOKEN, DB_API_URL, DB_LOGIN, DB_PASSWORD
from app.utils.database import Database

bot = Bot(token=BOT_API_TOKEN)
storage = JSONStorage(r'app/data/storage.json')
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())
db = Database(DB_API_URL, DB_LOGIN, DB_PASSWORD)
