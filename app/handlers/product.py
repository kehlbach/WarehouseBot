
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from app.data import callbacks as cb
from app.data.constants import DELETE, EDIT, VIEW
from app.keyboards import *
from app.loader import bot, db, dp
from app.utils import tools
from app.utils.processors import *

"""create edit_product_init"""


@dp.callback_query_handler(cb.generic.filter(state=Product.Edit.MENU), state='*')
async def edit_product_init(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    master_user_id = callback_query.from_user.id
    master = db.filter(db.PROFILES, user_id=master_user_id)
    permissions = tools.permissions(master)
    product_id = callback_data['data']
    if set([VIEW, EDIT, DELETE]).intersection(permissions[PRODUCTS]):
        product = db.get(db.PRODUCTS, product_id)
        text = 'Товар: ' + product['name']
        text += '\nАртикул (код товара): '+product['vendor_code']
        text += '\nКатегория: '+product['category_name']
        text += '\nЕдиницы измерения: '+product['units']
        reply_markup = edit_product(master, product=product)
    else:
        text = 'Нет доступа'
        reply_markup = None
    return await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@dp.callback_query_handler(
    cb.product_category.filter(action=(
        Product.Edit.Category.MENU,
        Product.Create.Category.MENU,
        Product.Edit.Category.SPECIFIC,
        Product.Create.Category.SPECIFIC
    )),
    state='*'
)
async def handle_product_edit_category(callback_query: CallbackQuery, callback_data: dict):
    action = callback_data['action']
    page = callback_data.get('page', 1)
    match action:
        case Product.Create.Category.MENU:
            text = 'Выберите категорию продукта:'
            categories_page = db.get_page(db.CATEGORIES, page)
            reply_markup = get_product_categories(
                Product.Create.Category, page, callback_data['product_id'], categories_page)
        case Product.Edit.Category.MENU:
            text = 'Выберите категорию продукта:'
            categories_page = db.get_page(db.CATEGORIES, page)
            reply_markup = get_product_categories(
                Product.Edit.Category, page, callback_data['product_id'], categories_page)
        case Product.Create.Category.SPECIFIC:
            text = 'Товар успешно создан'
            reply_markup = get_back(PRODUCTS, callback_data['product_id'])
            db.edit_patch(
                db.PRODUCTS, id=callback_data['product_id'], category=callback_data['category_id'])
        case Product.Edit.Category.SPECIFIC:
            changed_product = db.edit_patch(
                db.PRODUCTS, id=callback_data['product_id'], category=callback_data['category_id'])
            text = 'Категория успешно изменена на {}'.format(changed_product['category_name'])
            reply_markup = get_back(PRODUCTS, callback_data['product_id'])

    return await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@dp.callback_query_handler(cb.generic.filter(action=(Product.Edit.DELETE)), state='*')
async def handle_product_delete(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    product_id = callback_data['data']
    response = db.delete(db.PRODUCTS, id=product_id)
    reply_markup = get_back(PRODUCTS)
    if response.status_code == 204:
        text = 'Товар успешно удален.'
    elif 'ProtectedError' in response.text:
        reply_markup = get_back(PRODUCTS, id=product_id)
        text = 'Нельзя удалить товар, для которого заданы .'
    else:
        text = 'Произошла ошибка при удалении товара.'
        logging.warning('⭕тут чет товар не удалился')
    return await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )
