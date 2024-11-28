import logging

import requests.exceptions
import urllib3.exceptions
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils import exceptions

from app.keyboards.menu import get_back
from app.loader import bot, dp


@dp.message_handler(state="*", commands="cancel")
@dp.message_handler(Text(equals="cancel", ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.finish()
    await message.reply("Action canceled.", reply_markup=types.ReplyKeyboardRemove())


@dp.errors_handler()
async def general_error_handler(update: types.Update, exception: Exception):
    match exception:
        case (
            requests.exceptions.ConnectionError()
            | urllib3.exceptions.NewConnectionError()
        ):
            if "callback_query" in update:
                chat_id = update.callback_query.message.chat.id
            elif "message" in update:
                chat_id = update.message.chat.id
            logging.error(f"⭕ Нет подключения к базе данных")
            return await bot.send_message(chat_id, "No connection to database")
        case exceptions.MessageNotModified:
            logging.error(f"⭕ Message not modified")
        case PermissionError():
            state = dp.current_state()
            await state.finish()
            message_text = "You don't have permission to perform this action"
            if "callback_query" in update:
                try:
                    await bot.edit_message_text(
                        chat_id=update.callback_query.message.chat.id,
                        message_id=update.callback_query.message.message_id,
                        text=message_text,
                        reply_markup=get_back(),
                    )
                except:
                    pass
            elif "message" in update:
                return await update.message.answer(message_text)
        case _:
            logging.exception(f"⭕Exception {exception} Exception⭕")
            logging.error(f"\nTraceback ends⭕")
            return None
