import json
from aiogram import __main__ as aiogram_core
from aiogram import filters, md, types
from aiogram.dispatcher.webhook import SendMessage
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext
from math import ceil
from types import SimpleNamespace
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from app.data.callbacks import base
from app.keyboards import get_user_departments, get_user_roles
from app.loader import bot, dp, db
from app.data.constants.subjects import ALL_DEPARTMENTS
from app.keyboards import *
from app.data.states import User
from app.utils import tools



# menu_to_option = {
#     Menu.PROFILES: get_profiles,
#     User.Create.Departments.MENU: get_user_departments,
#     User.Edit.Departments.MENU: get_user_departments
# }



# menu_option_resolver = lambda action: menu_option_resolver(action)



# @dp.callback_query_handler(base.filter(action='prev_page'), state='*')
# async def process_prev_page(callback_query: CallbackQuery, callback_data):
#     #callback_data['data'] = json.loads(callback_data['data'])
#     action = callback_data['action']
#     get_keyboard = menu_option_resolver(action)
#     user_id = callback_query.from_user.id
#     profile = db.get(PROFILES,user_id)

#     return await bot.edit_message_text(
#         chat_id=callback_query.message.chat.id,
#         message_id=callback_query.message.message_id,
#         **get_subject_entities(master=profile,state=callback_data['subject'],page=int(callback_data['page'])-1))


#     if keyboard == KB_SUBJECT_ENTITIES:
        
#     elif keyboard == KB_USER_ROLES:
#         return await bot.edit_message_text(
#             chat_id=callback_query.message.chat.id,
#             message_id=callback_query.message.message_id,
#             **get_user_roles(master=profile,action_class=callback_data['action'],page=int(callback_data['page'])-1))
    

# @dp.callback_query_handler(base.filter(action='curr_page'), state='*')
# async def process_curr_page(callback_query: CallbackQuery, callback_data):
#     callback_data['data'] = json.loads(callback_data['data'])
#     keyboard = callback_data['keyboard']
#     if keyboard == KB_SUBJECT_ENTITIES:
#         count = db.get_page(callback_data['subject'],callback_data['page'])['count']
#         pages = ceil(count/10)
#         return await callback_query.answer(f'Всего {pages} страниц')
    

# @dp.callback_query_handler(base.filter(action='next_page'), state='*')
# async def process_next_page(callback_query: CallbackQuery, callback_data):
#     callback_data['data'] = json.loads(callback_data['data'])
#     keyboard = callback_data['keyboard']
#     user_id = callback_query.from_user.id
#     profile = db.get(PROFILES,user_id)
#     if keyboard == KB_SUBJECT_ENTITIES:
#         return await bot.edit_message_text(
#             chat_id=callback_query.message.chat.id,
#             message_id=callback_query.message.message_id,
#             **get_subject_entities(master=profile,state=callback_data['subject'],page=int(callback_data['page'])+1))
#     elif keyboard == KB_USER_ROLES:
#         return await bot.edit_message_text(
#             chat_id=callback_query.message.chat.id,
#             message_id=callback_query.message.message_id,
#             **get_user_roles(master=profile,action_class=callback_data['action'],page=int(callback_data['page'])+1))
    