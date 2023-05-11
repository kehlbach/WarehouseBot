import logging
import os
# from asyncio import sleep
from datetime import datetime
import re
import phonenumbers
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher
from aiogram import __main__ as aiogram_core
from aiogram import filters, md, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.webhook import SendMessage
from aiogram.types import KeyboardButton, ParseMode, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram.utils import exceptions
from app.loader import bot, dp, db
from app.keyboards import *
from app.utils.config import ADMIN_NUMBER
from app.utils.processors import NAME_PATTERN
# from .admin import Admin
from app.data.states import *
from app.data.constants import *
import requests.exceptions  
import urllib3.exceptions
from app.utils.processors import *
#@dp.message_handler()

WELCOME = lambda master:'Добро пожаловать.\n' +\
            'Ваша роль - '+master['role_name']

def _prepare_menu(master):
    permissions = tools.permissions(master)
    if master and any(permissions.values()):
        text = 'Добро пожаловать.\n' +\
            'Ваша роль - '+master['role_name']
        permissions = tools.permissions(master)
        reply_markup = get_main_menu(master)
    elif master:
        text = 'Роль еще не установлена'
        keyboard = InlineKeyboardMarkup()
        reply_markup = kb_check_status
    else:
        text = 'Вы не зарегистрированы в системе.\n' +\
            '/start чтобы зарегистрироваться'
        reply_markup = None
    return {'text':text, 'reply_markup':reply_markup}
    

@dp.message_handler(commands='start', state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    """
    Conversation's entry point
    """
    await state.finish()
    user_id = message.from_id    

    profile = db.filter(db.PROFILES, user_id=user_id)
    if profile and profile['name']:
        await message.answer(**_prepare_menu(profile))
    elif profile:
        await Login.name.set()
        data = {'id':profile['id']}
        await state.set_data(data)
        text = 'Введите ФИО. Пример:\nИванов Иван Иванович'
        return await message.answer(text) 
    else:
        await Login.number.set()
        return await message.answer("Поделитесь номером телефона .", reply_markup=kb_send_number)


@dp.message_handler(state=Login.number, content_types=types.ContentType.CONTACT)
@tools.has_permissions()
async def process_number(message: types.Message, state: FSMContext):
    formatted_number , is_valid, error_text = number_preprocessor(message=message,login=True)
    if not is_valid:
        return await message.answer(error_text)
    profile = db.filter(db.PROFILES, phone_number=formatted_number)   
    if profile:
        if profile['name']:
            await state.finish()
            profile = db.edit_patch(db.PROFILES,profile['id'],user_id=message.from_id)
            return await message.answer(**_prepare_menu(profile))
    else:
        profile = db.add(
            db.PROFILES,
            phone_number = formatted_number,
            role = db.filter(db.ROLES,name='Без прав')['id'],
            user_id = message.from_id
        )
    data = {'id':profile['id']}
    await state.set_data(data)
    # async with state.proxy() as data:
    #     data['id']= profile['id']
    await Login.name.set()
    text = 'Введите ФИО. Пример:\nИванов Иван Иванович'
    return await message.answer(text)     


    

#@dp.message_handler(state=UserEdit.name)
@dp.message_handler(state=Login.name)
async def process_name(message: types.Message, state: FSMContext):
    name, is_valid, error_text = name_validator(message.text)
    if not is_valid:
        return await message.answer(error_text)
    data = await state.get_data()
    profile = db.edit_patch(db.PROFILES,id = data['id'], name=name)
    await state.finish()
    return await message.answer(**_prepare_menu(profile))




# @dp.message_handler(lambda message: message.text == 'Проверить статус', state=Login.check)
@dp.callback_query_handler(cb.action.filter(action=Login.CHECK), state='*')
async def check_status(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query['from']['id']
    profile = db.filter(db.PROFILES, user_id=user_id)
        #await User.menu.set()
    await state.finish()
    menu = _prepare_menu(profile)
    if menu['reply_markup'] == callback_query.message.reply_markup:
        await callback_query.answer('Роль еще не установлена')
    else:
        await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=menu['text'],
        reply_markup=menu['reply_markup'])






@dp.errors_handler()  # handle the cases when this exception raises 
async def general_error_handler(update, exception):
    match exception:
        case requests.exceptions.ConnectionError() | urllib3.exceptions.NewConnectionError():
            chat_id = update.message.from_id
            logging.error(f'⭕ Нет подключения к базе данных')
            return await bot.send_message(chat_id, 'Нет соединения с базой данных')
        case exceptions.MessageNotModified:
            logging.error(f'⭕ Message not modified')
        case _:
            logging.exception(f'⭕Exception {exception} Exception⭕')
            logging.error(f'\nTraceback ends⭕')
            return None
        





# @dp.callback_query_handler(state='*')
# async def hey(callback_query: types.Message, state: FSMContext):
#     logging.error('🟠Хеееей')
#     # await callback_query.message.answer(callback_query.data)


# @dp.message_handler(state=Login.input_login)
# async def process_login(message: types.Message, state: FSMContext):
#     """
#     Process user name
#     """
#     async with state.proxy() as data:
#         data['login'] = message.text
#     await Login.next()
#     await message.reply("And Your Password:")

# @dp.message_handler(state=Login.input_password)
# async def process_password(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         response = session.get(DB_API_URL+'/profiles/?login='+data['login']).json()
#         if response['count'] == 1:
#             profile = response['results'][0]
#             resp_pass = profile['password']
#             inp_pass = message.text
#             if pbkdf2_sha256.verify(inp_pass,resp_pass):
#                 await message.reply("Вы должны были успешно войти")
#                 chats_response = session.post(DB_API_URL + '/chats/',data={
#                     'chat_id':message['chat'].id,
#                     'profile':r'http://127.0.0.1:8000/profiles/'+str(profile['id'])})
#                 if chats_response.status_code:
#                     await LoggedIn.menu.set()
#                     markup = get_menu()
#                     await message.reply("Вы успешно вошли",reply_markup=markup)
#                     return
#                     #Добавить кнопки
#         await Login.input_login.set()
#         await message.reply("Your login or password is incorrect. Try again.\n Login:")

#         #if pbkdf2_sha256.verify("password", hash)

# @dp.message_handler(state=LoggedIn.menu)
# async def show_menu(message:types.Message, state: FSMContext):
#     pass

# @dp.message_handler(state='*', commands='logout')
# @dp.message_handler(lambda message: message.text == 'Выйти', state=LoggedIn.menu)
# async def logout(message:types.Message, state: FSMContext):
#     try:
#         response = session.delete(DB_API_URL + '/chats/'+message['chat'].id)
#         Login.input_login.set()
#     except:
#         pass


#####


# throttled = "Too many requests, relax!"


# # start, help command handler
# @dp.message_handler(filters.Command(commands=["start", "help"], prefixes="!/", ignore_case=False))
# @dp.throttled(
#     lambda msg, loop, *args, **kwargs: loop.create_task(
#         bot.send_message(
#             msg.from_user.id,
#             throttled,
#             parse_mode=types.ParseMode.MARKDOWN,
#             reply_to_message_id=msg.message_id,
#         )
#     ),
#     rate=2,
# )
# async def cmd_start(message: types.Message) -> None:
#     await bot.send_message(
#         message.from_user.id,
#         "Welcome!",
#         parse_mode=types.ParseMode.MARKDOWN,
#     )


# # version command handler
# @dp.message_handler(
#     filters.Command(commands=["v", "version"], prefixes="!/", ignore_case=False),
#     content_types=types.ContentType.TEXT,
# )
# @dp.throttled(
#     lambda msg, loop, *args, **kwargs: loop.create_task(
#         bot.send_message(
#             msg.from_user.id,
#             throttled,
#             parse_mode=types.ParseMode.MARKDOWN,
#             reply_to_message_id=msg.message_id,
#         )
#     ),
#     rate=2,
# )
# async def cmd_version(message: types.Message) -> None:
#     await message.reply("My Engine\n{api_info}".format(api_info=md.quote_html(str(aiogram_core.SysInfo()))))


# # messages equals handler
# @dp.message_handler(
#     filters.Text(
#         equals=[
#             "hi",
#             "hello",
#             "hey",
#             "hallo",
#             "hei",
#             "helo",
#             "hola",
#             "privet",
#             "hai",
#         ],
#         ignore_case=True,
#     ),
#     content_types=types.ContentType.TEXT,
# )
# async def text_equals(message: types.Message) -> None:
#     await sleep(1)
#     await types.ChatActions.typing()
#     await message.reply(message.text)


# # any type messages handler
# @dp.message_handler(content_types=types.ContentType.ANY)
# async def any_messages(message: types.Message) -> None:
#     #if SERVERLESS is True:
#     #    return SendMessage(message.chat.id, "🤔")
#     #else:
#     await bot.send_message(message.chat.id, "🤔")
