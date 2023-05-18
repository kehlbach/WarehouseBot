
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from app import keyboards as kb
from app.data import callbacks as cb
from app.data.constants import *
from app.data.states import *
from app.keyboards import *
from app.keyboards.category import get_categories
from app.loader import bot, db, dp
from app.utils import tools
from aiogram.utils.exceptions import BadRequest
from .login import _prepare_menu


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
            departments_page = db.get_page(db.DEPARTMENTS,callback_data.get('page',1))
            text = 'Выберите отделение для просмотра остатков'
            reply_markup = get_inventory_department(master, departments_page, callback_data.get('page',1))
        case Menu.RECEIPTS:
            departments_page = db.get_page(db.DEPARTMENTS,callback_data.get('page',1))
            text = 'Выберите отделение для просмотра накладных'
            reply_markup = get_receipt_department(master, departments_page, callback_data.get('page',1))
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

    try:
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text= text,
            reply_markup=reply_markup)
    except BadRequest:
        await bot.delete_message(
            chat_id=callback_query.message.chat.id, 
            message_id=callback_query.message.message_id)
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=text,
            reply_markup=reply_markup
        )



@dp.callback_query_handler(cb.menu_item.filter(state=CURRENT_PAGE), state='*')
async def process_current_page(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    page = callback_data['page']
    await callback_query.answer('{} страница.'.format(page))