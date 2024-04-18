from os import path
from pathlib import Path

from envparse import env

app_dir: Path = Path(__file__).parent.parent
env_file = app_dir / ".env"
if path.isfile(env_file):
    env.read_envfile(env_file)
BOT_API_TOKEN = env.str("API_TOKEN", default="")
SERVERLESS = env.bool("SERVERLESS", default=False)
WEBHOOK_HOST = env.str("WEBHOOK_HOST", default="")
WEBHOOK_PATH = env.str("WEBHOOKPATH", default="")
WEBAPP_HOST = env.str("WEBAPP_HOST", default="0.0.0.0")
WEBAPP_PORT = env.int("WEBAPP_PORT", default=3000)
DB_API_URL = env.str("DB_API_URL", default='127.0.0.1:8000/')
DB_LOGIN = env.str("DB_LOGIN")
DB_PASSWORD = env.str("DB_PASSWORD")
ADMIN_NUMBER = env.str('ADMIN_NUMBER')
NGROK = env.str('NGROK')
COUNTRY_CODE = env.str('COUNTRY_CODE')
