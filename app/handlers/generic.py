from json import loads

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from app.data import callbacks as cb
from app.data.constants import (CATEGORIES, DEPARTMENTS, PRODUCTS, PROFILES,
                                ROLES,RECEIPTS)
from app.data.states import Category, Department, Generic, Product, Role, User, Receipt
from app.keyboards import get_back, kb_skip
from app.keyboards.department import edit_department_location
from app.keyboards.product import get_product_categories, kb_get_units
from app.keyboards.role import get_role_permissions
from app.keyboards.user import get_user_roles
from app.loader import db, dp
from app.utils.processors import *


@dp.callback_query_handler(cb.generic.filter(state=Generic.CALLBACK_TO_MESSAGE_INIT), state='*')
async def generic_message_request(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['data'] and isinstance(callback_data['data'], str):
        callback_data['data'] = loads(callback_data['data'])
    action = callback_data['action']
    get_text = {
        User.Edit.NAME: 'Введите ФИО. Пример:\n Иванов Иван Иванович',
        User.Edit.NUMBER: 'Введите новый номер мобильного телефона:',
        User.Create.NUMBER: 'Введите номер мобильного телефона пользователя:',
        User.Edit.NUMBER_OWN: 'Введите новый номер мобильного телефона:',
        Category.Create.NAME: 'Введите имя категории:',
        Category.Edit.NAME: 'Введите имя категории:',
        Department.Create.NAME: 'Введите название отделения:',
        Department.Edit.NAME: 'Введите название отделения:',
        Department.Edit.LOCATION: 'Введите адрес отделения:',
        Role.Create.NAME: 'Введите название роли:',
        Role.Edit.NAME: 'Введите название роли:',
        Product.Create.VENDOR_CODE: 'Введите артикул (код товара):',
        Product.Create.NAME: 'Введите наименование товара:',
        Product.Create.UNIT: 'Введите единицу измерения:',
        Product.Edit.NAME: 'Введите наименование товара:',
        Product.Edit.UNIT: 'Введите или выберите единицу измерения:',
        Product.Edit.VENDOR_CODE: 'Введите артикул (код товара):',
        Receipt.Edit.NOTE: 'Введите примечание:',
    }

    get_reply_markup = {
        Department.Create.LOCATION: kb_skip,
        Department.Edit.LOCATION: edit_department_location,
        Product.Create.VENDOR_CODE: kb_skip,
        Product.Create.UNIT: kb_get_units,
        Product.Edit.UNIT: kb_get_units,
    }

    get_data_names = {
        User.Edit.NAME: ['profile_id'],
        User.Edit.NUMBER: ['profile_id', 'source_number'],
        User.Edit.NUMBER_OWN: ['profile_id', 'source_number'],
        Category.Edit.NAME: ['category_id'],
        Department.Edit.NAME: ['department_id'],
        Department.Edit.LOCATION: ['department_id'],
        Role.Edit.NAME: ['role_id'],
        Product.Edit.NAME: ['product_id'],
        Product.Edit.UNIT: ['product_id'],
        Product.Edit.VENDOR_CODE: ['product_id'],
        Receipt.Edit.NOTE: ['receipt_id']
    }

    reply_markup = get_reply_markup.get(action, None)
    await Generic.message_handle.set()
    async with state.proxy() as data:
        data['state'] = callback_data['state']
        data['action'] = callback_data['action']
        callback_iter = iter(callback_data['data'])
        for each in get_data_names.get(action, []):
            data[each] = next(callback_iter)
        return await callback_query.message.answer(
            text=get_text[action],
            reply_markup=reply_markup
        )


@dp.message_handler(state=Generic.message_handle)
async def generic_message_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    action = data['action']
    processed_data: str = ''
    db_response: dict = {}

    get_data_processor = {
        User.Edit.NAME: lambda: name_validator(message.text),
        User.Edit.NUMBER: lambda: number_preprocessor(message, data['source_number']),
        User.Create.NUMBER: lambda: number_preprocessor(message),
        User.Edit.NUMBER_OWN: lambda: number_preprocessor(message, data['source_number']),
        Department.Edit.LOCATION: lambda: ('', True, '') if message.text == 'Убрать адрес' else (message.text, True, '')

    }
    get_db_condition = {
        Department.Create.LOCATION: lambda: False if processed_data == 'Пропустить' else True,
    }

    get_db_operation = {
        User.Edit.NAME: lambda: db.edit_patch(
            db.PROFILES,
            data['profile_id'],
            requester=message.chat.id,
            name=processed_data),
        User.Edit.NUMBER: lambda: db.edit_patch(
            db.PROFILES,
            data['profile_id'],
            requester=message.chat.id,
            phone_number=processed_data,
            user_id=processed_data),
        User.Create.NUMBER: lambda: db.add(
            db.PROFILES,
            requester=message.chat.id,
            phone_number=processed_data,
            role=db.filter(db.ROLES, name='Без прав')['id'],
            user_id=processed_data
        ),
        User.Edit.NUMBER_OWN: lambda: db.edit_patch(
            db.PROFILES,
            data['profile_id'],
            requester=message.chat.id,
            phone_number=processed_data,
            user_id=processed_data),
        Category.Create.NAME: lambda: db.add(
            db.CATEGORIES,
            requester=message.chat.id,
            name=processed_data
        ),
        Category.Edit.NAME: lambda: db.edit_patch(
            db.CATEGORIES,
            data['category_id'],
            requester=message.chat.id,
            name=processed_data
        ),
        Department.Create.NAME: lambda: db.add(
            db.DEPARTMENTS,
            requester=message.chat.id,
            name=processed_data
        ),
        Department.Create.LOCATION: lambda: db.edit_patch(
            db.DEPARTMENTS,
            data['department']['id'],
            requester=message.chat.id,
            location=processed_data
        ),
        Department.Edit.NAME: lambda: db.edit_patch(
            db.DEPARTMENTS,
            data['department_id'],
            requester=message.chat.id,
            name=processed_data
        ),
        Department.Edit.LOCATION: lambda: db.edit_patch(
            db.DEPARTMENTS,
            data['department_id'],
            requester=message.chat.id,
            location=processed_data
        ),
        Role.Create.NAME: lambda: db.add(
            db.ROLES,
            requester=message.chat.id,
            name=processed_data
        ),
        Role.Edit.NAME: lambda: db.edit_patch(
            db.ROLES,
            data['role_id'],
            requester=message.chat.id,
            name=processed_data
        ),
        Product.Create.NAME: lambda: db.add(
            db.PRODUCTS,
            requester=message.chat.id,
            name=processed_data,
            vendor_code=data['vendor_code'],
            category=''
        ),

        Product.Create.UNIT: lambda: db.edit_patch(
            db.PRODUCTS,
            data['product_id'],
            requester=message.chat.id,
            units=processed_data
        ),
        Product.Edit.NAME: lambda: db.edit_patch(
            db.PRODUCTS,
            data['product_id'],
            requester=message.chat.id,
            name=processed_data
        ),
        Product.Edit.VENDOR_CODE: lambda: db.edit_patch(
            db.PRODUCTS,
            data['product_id'],
            requester=message.chat.id,
            vendor_code=processed_data
        ),
        Product.Edit.UNIT: lambda: db.edit_patch(
            db.PRODUCTS,
            data['product_id'],
            requester=message.chat.id,
            units=processed_data
        ),
        Receipt.Edit.NOTE: lambda: db.edit_patch(
            db.RECEIPTS,
            data['receipt_id'],
            requester=message.chat.id,
            note=processed_data
        )
    }

    get_next_action = {
        Product.Create.VENDOR_CODE: Product.Create.NAME,
        Product.Create.NAME: Product.Create.UNIT,
        Product.Create.UNIT: Product.Create.Category.MENU,
        Department.Create.NAME: Department.Create.LOCATION
    }

    set_state = {
        Department.Create.NAME: lambda: Generic.message_handle.set(),
        Product.Create.VENDOR_CODE: lambda: Generic.message_handle.set(),
        Product.Create.NAME: lambda: Generic.message_handle.set(),
    }
    set_state_data = {
        Department.Create.NAME: lambda: state.set_data({'department': db_response, **data}),
        Product.Create.VENDOR_CODE: lambda: state.set_data({'vendor_code': processed_data, **data}),
        Product.Create.NAME: lambda: state.set_data({'product_id': db_response['id'], **data}),
    }

    get_text = {
        User.Edit.NAME: lambda: 'Имя пользователя изменено на {}.'.format(db_response['name']),
        User.Create.NUMBER: lambda: 'Выберите роль пользователя:',
        User.Edit.NUMBER: lambda: 'Номер изменен на {}.'.format(db_response['phone_number']),
        User.Edit.NUMBER_OWN: lambda: 'Номер изменен на {}.'.format(db_response['phone_number']) +
        '\nТеперь вы можете войти с другого аккаунта Telegram.',
        Category.Create.NAME: lambda: 'Категория "{}" создана.'.format(db_response['name']),
        Category.Edit.NAME: lambda: 'Название категории изменено на "{}".'.format(db_response['name']),
        Department.Create.NAME: lambda: 'Введите адрес отделения:',
        Department.Create.LOCATION: lambda: 'Отделение "{}"создано:'.format(data['department']['name']),
        Department.Edit.NAME: lambda: 'Название отделения изменено на "{}".'.format(db_response['name']),
        Department.Edit.LOCATION: lambda: 'Адрес отделения изменен на "{}".:'.format(db_response['location']),
        Role.Create.NAME: lambda: 'Теперь задайте разрешения для роли.',
        Role.Edit.NAME: lambda: 'Название роли изменено на "{}".'.format(db_response['name']),
        Product.Create.VENDOR_CODE: lambda: 'Введите наименование товара: ',
        Product.Create.NAME: lambda: 'Введите или выберите единицу измерения: ',
        Product.Create.UNIT: lambda: 'Выберите категорию: ',
        Product.Edit.NAME: lambda: 'Название товара изменено на "{}".'.format(db_response['name']),
        Product.Edit.VENDOR_CODE: lambda: 'Артикул (код товара) товара изменен на "{}".'.format(db_response['vendor_code']),
        Product.Edit.UNIT: lambda: 'Единицы измерения товара изменены на "{}".'.format(db_response['units']),
        Receipt.Edit.NOTE: lambda: 'Примечание было изменено на "{}".'.format(db_response['note']),
    }
    get_reply_markup = {
        User.Edit.NAME: lambda: get_back(PROFILES, data['profile_id']),
        User.Edit.NUMBER: lambda: get_back(PROFILES, data['profile_id']),
        User.Create.NUMBER: lambda: get_user_roles(
            User.Create.Roles,
            1,
            db_response['id'],
            db.get_page(db.ROLES)),
        User.Edit.NUMBER_OWN: lambda: get_back(PROFILES, data['profile_id']),
        Category.Create.NAME: lambda: get_back(CATEGORIES, db_response['id']),
        Category.Edit.NAME: lambda: get_back(CATEGORIES, data['category_id']),
        Department.Create.NAME: lambda: kb_skip,
        Department.Create.LOCATION: lambda: get_back(DEPARTMENTS, data['department']['id']),
        Department.Edit.NAME: lambda: get_back(DEPARTMENTS, data['department_id']),
        Department.Edit.LOCATION: lambda: get_back(DEPARTMENTS, data['department_id']),
        Role.Create.NAME: lambda: get_role_permissions(Role.Create.Permissions, db_response),
        Role.Edit.NAME: lambda: get_back(ROLES, data['role_id']),
        Product.Create.UNIT: lambda: get_product_categories(
            Product.Create.Category,
            1,
            db_response['id'],
            db.get_page(db.CATEGORIES)),
        Product.Create.NAME: lambda: kb_get_units,
        Product.Edit.NAME: lambda: get_back(PRODUCTS, data['product_id']),
        Product.Edit.VENDOR_CODE: lambda: get_back(PRODUCTS, data['product_id']),
        Product.Edit.UNIT: lambda: get_back(PRODUCTS, data['product_id']),
        Receipt.Edit.NOTE: lambda: get_back(RECEIPTS, [db_response['to_department'],data['receipt_id']]),
    }

    process_input = get_data_processor.get(action, lambda: (message.text, True, ''))
    processed_data, is_valid, error_text = process_input()

    if not is_valid:
        return await message.answer(error_text)
    db_condition = get_db_condition.get(action, lambda: True)
    if db_condition():
        execute_db_operation = get_db_operation.get(action, lambda: None)
        db_response = execute_db_operation()
    if db_response and 'already exists' in str(db_response.values()):
        return await message.answer('Объект с такими данными уже существует.')

    data['action'] = get_next_action.get(action, action)
    await set_state.get(action, state.finish)()
    if action in set_state_data.keys():
        await set_state_data[action]()
    reply_markup = get_reply_markup.get(action, lambda: None)()
    if reply_markup:
        return await message.answer(text=get_text[action](), reply_markup=reply_markup,)
    else:
        return await message.answer(text=get_text[action](),)
