import logging
from urllib.parse import urljoin

from aiogram import Dispatcher, executor, types
from pyngrok import ngrok

from app.utils.config import (NGROK, SERVERLESS, WEBAPP_HOST, WEBAPP_PORT,
                              WEBHOOK_HOST, WEBHOOK_PATH)
from app.loader import bot, dp


logging.basicConfig(level=logging.INFO)


async def on_startup(dispatcher: Dispatcher) -> None:
    if SERVERLESS:
        if NGROK:
            WEBHOOK_PATH = ''
            ngrok.connect(WEBAPP_PORT)
            urls = list(i.public_url for i in ngrok.get_tunnels()
                        if 'https' in i.public_url)
            WEBHOOK_URL = [i for i in urls if 'https' in i][0]
            logging.info('Ngrok URL received.')
        else:
            WEBHOOK_URL = urljoin(WEBHOOK_HOST, WEBHOOK_PATH)
        logging.info("🟢 Bot launched as Serverless!")
        logging.info(f"webhook: {WEBHOOK_URL}")
        webhook = await dispatcher.bot.get_webhook_info()
        if webhook.url:
            await bot.delete_webhook()
        await bot.set_webhook(WEBHOOK_URL)
    else:
        logging.info("🟢 Bot launched!")
    await dispatcher.bot.set_my_commands([types.BotCommand(command="/start", description="Start the bot")])


async def on_shutdown(dispatcher: Dispatcher) -> None:
    logging.warning("🟠 Bot shutdown...")
    if SERVERLESS is True:
        await bot.delete_webhook()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


def bot_register(webhook: bool = False) -> None:
    try:
        import app.handlers
        if SERVERLESS and webhook:
            executor.start_webhook(
                dispatcher=dp,
                webhook_path=WEBHOOK_PATH,
                on_startup=on_startup,
                on_shutdown=on_shutdown,
                skip_updates=True,
                host=WEBAPP_HOST,
                port=WEBAPP_PORT,
            )
        else:
            executor.start_polling(
                dp,
                skip_updates=True,
                on_startup=on_startup,
                on_shutdown=on_shutdown,
            )
        return
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.exception(e)


if __name__ == '__main__':
    bot_register(True)
