
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from app.data import callbacks as cb
from app.data.constants import *
from app.data.constants import DELETE, EDIT, VIEW
from app.data.states import Department
from app.keyboards import edit_department, get_back
from app.loader import bot, db, dp
from app.utils import tools
from app.utils.processors import *


@dp.callback_query_handler(cb.generic.filter(state=Department.Edit.MENU), state='*')
async def edit_department_init(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    master_user_id = callback_query.from_user.id
    master = db.filter(db.PROFILES, user_id=master_user_id)
    permissions = tools.permissions(master)
    department_id = callback_data['data']
    if set([VIEW, EDIT, DELETE]).intersection(permissions[DEPARTMENTS]):
        department = db.get(db.DEPARTMENTS, department_id)
        text = 'Отделение: ' + department['name'] +\
               '\nАдрес: ' + department['location']
        reply_markup = edit_department(
            master,
            department=department,
        )
    return await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@dp.callback_query_handler(cb.generic.filter(action=(Department.Edit.DELETE)), state='*')
async def handle_department_delete(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    department_id = callback_data['data']
    response = db.delete(
        db.DEPARTMENTS, 
        id=department_id,
        requester=callback_query.message.chat.id,
        raise_error=False)
    reply_markup = get_back(DEPARTMENTS)
    if response.status_code == 204:
        text = 'Отделение успешно удалено.'
    elif response.status_code==403:
        text = 'Нет прав на удаление отделения.'
    elif 'ProtectedError' in response.text:
        reply_markup = get_back(DEPARTMENTS, department_id)
        text = 'Нельзя удалить отделение, если в остатках в нем есть товары.'
    else:
        text = 'Произошла ошибка при удалении отделения.'
        logging.warning('⭕тут чет категория не удалилась')

    return await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )
