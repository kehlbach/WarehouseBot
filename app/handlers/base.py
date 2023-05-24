import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.data.constants import *
from app.data.states import *
from app.keyboards import *
from app.loader import dp, bot
from app.utils.processors import *

import logging
import requests.exceptions
import urllib3.exceptions
from aiogram.utils import exceptions

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply('Операция отменена.', reply_markup=types.ReplyKeyboardRemove())

@dp.errors_handler()
async def general_error_handler(update, exception):
    match exception:
        case requests.exceptions.ConnectionError() | urllib3.exceptions.NewConnectionError():
            if 'callback_query' in update:
                chat_id = update.callback_query.message.chat.id
            elif 'message' in update:
                chat_id = update.message.chat.id
            logging.error(f'⭕ Нет подключения к базе данных')
            return await bot.send_message(chat_id, 'Нет соединения с базой данных')
        case exceptions.MessageNotModified:
            logging.error(f'⭕ Message not modified')
        case PermissionError():
            if 'callback_query' in update:
                return await update.callback_query.answer('Недостаточно прав для выполнения данного действия')
            elif 'message' in update:
                return await update.message.answer('Недостаточно прав для выполнения данного действия')
        case _:
            logging.exception(f'⭕Exception {exception} Exception⭕')
            logging.error(f'\nTraceback ends⭕')
            return None
