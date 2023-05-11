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
#from app.data.cb import cb.base
from app.data import callbacks as cb
from app.keyboards.category import get_categories
from app.keyboards.user import get_profiles
from app.loader import bot, dp, db
from app.data.constants.subjects import ALL_DEPARTMENTS
from app.keyboards import *
from app import keyboards as kb
from app.data.states import *
from app.data.constants import *
from app.utils import tools
from copy import deepcopy
# class User(StatesGroup):
#    menu = State()
from .login import _prepare_menu

# class Menu (StatesGroup):
#     main = State()
#     users1 = State

# @dp.callback_query_handler(lambda callback_query: callback_query.data == 'main_menu', state=User.menu)
# #@dp.message_handler(state=User.menu)
# async def process_menu_1(callback_query: CallbackQuery, state: FSMContext):
#     await callback_query.answer("I see U:")
#     await callback_query.message.answer(callback_query.data)
@dp.callback_query_handler(cb.action.filter(action=Menu.INIT), state='*')
@dp.callback_query_handler(cb.action.filter(action=Login.CHECK),state='*')
async def process_menu_init(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = callback_query['from']['id']
    master = db.filter(db.PROFILES, user_id=user_id)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        **_prepare_menu(master)
    )
    



@dp.callback_query_handler(cb.menu_item.filter(state=Menu.CHOICE), state='*')
@tools.has_permissions()
async def process_menu_choice(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = callback_query['from']['id']
    master = db.filter(db.PROFILES, user_id=user_id)
    match callback_data['action']:
        case Menu.PROFILES:
            profiles_page = db.get_page(db.PROFILES,callback_data.get('page',1))
            text = 'Выберите пользователя'
            reply_markup = kb.get_profiles(master,profiles_page, callback_data.get('page',1))
        case Menu.ROLES:
            roles_page = db.get_page(db.ROLES,callback_data.get('page',1))
            text = 'Выберите роль'
            reply_markup = kb.get_roles(master,roles_page, callback_data.get('page',1))
        case Menu.INVENTORY:
            pass
        case Menu.RECEIPTS:
            pass
        case Menu.PRODUCTS:
            products_page = db.get_page(db.PRODUCTS,callback_data.get('page',1))
            text = 'Выберите товар'
            reply_markup = get_products(master,products_page, callback_data.get('page',1))
        case Menu.CATEGORIES:
            categories_page = db.get_page(db.CATEGORIES,callback_data.get('page',1))
            text = 'Выберите категорию'
            reply_markup = get_categories(master,categories_page, callback_data.get('page',1))
        case Menu.DEPARTMENTS:
            departments_page = db.get_page(db.DEPARTMENTS,callback_data.get('page',1))
            text = 'Выберите отделение'
            reply_markup = kb.get_departments(master,departments_page, callback_data.get('page',1))


    return await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text= text,
        reply_markup=reply_markup)



@dp.callback_query_handler(cb.menu_item.filter(state=CURRENT_PAGE), state='*')
async def process_current_page(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    page = callback_data['page']
    await callback_query.answer('{} страница.'.format(page))




# @dp.callback_query_handler(cb.base.filter())
# async def catcher(callback_query: CallbackQuery, callback_data):
#     #callback_data['data'] = json.loads(callback_data['data'])
#     return await callback_query.answer('Срок действия кнопки истек.')

