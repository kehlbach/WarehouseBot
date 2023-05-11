
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from app.data.constants import *
from app.data import callbacks as cb
from app.data.constants import DELETE, EDIT, PROFILES, VIEW
from app.keyboards import *
from app.loader import bot, db, dp
from app.data.states import category
from app.utils import tools
from app.utils.processors import *


@dp.callback_query_handler(cb.generic.filter(state=Category.Edit.MENU), state='*')
async def edit_category_init (callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    master_user_id = callback_query.from_user.id
    master = db.filter(db.PROFILES, user_id=master_user_id)
    permissions = tools.permissions(master)
    category_id=callback_data['data']
    if set([VIEW, EDIT, DELETE]).intersection(permissions[ROLES]):
        category = db.get(db.CATEGORIES, category_id)
        text = 'Категория: ' + category['name']
        reply_markup = edit_category(
            master,
            category=category,
        )
    return await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@dp.callback_query_handler(cb.generic.filter(action=(Category.Edit.DELETE)), state='*')
async def handle_category_delete(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    category_id = callback_data['data']
    response = db.delete(db.CATEGORIES, id=category_id)
    reply_markup = get_back(CATEGORIES)
    if response.status_code == 204:
        text = 'Категория успешно удалена.'
    elif 'ProtectedError' in response.text:
        reply_markup = get_back(CATEGORIES,id=category_id)
        text = 'Нельзя удалить категорию, содержащую товары.'
    else:
        text = 'Произошла ошибка при удалении категории.'
        logging.warning('⭕тут чет категория не удалилась')
    
    return await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )
