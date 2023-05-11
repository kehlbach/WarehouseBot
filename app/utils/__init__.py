# isort:skip_file
# flake8: noqa
NAME_PATTERN = r'([А-Я]{1}[а-я]+) ([А-Я]{1}[а-я]+) ([А-Я]{1}[а-я]+)'

from . import config, processors, tools
from .tools import NAME_PATTERN
from .config import DB_API_URL, DB_LOGIN, DB_PASSWORD
from app.loader import bot, db, dp

