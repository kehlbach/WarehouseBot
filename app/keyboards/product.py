from app.data import callbacks as cb
from app.data.constants import ADD, DELETE, EDIT, PRODUCTS, VIEW
from app.data.constants.actions import ALL_ACTIONS
from app.data.constants.subjects import ALL_SUBJECTS
from app.data.states import Generic, Menu, Product
from app.keyboards.menu import _get_pages, get_back
from app.utils import tools

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


from copy import deepcopy
from json import dumps, loads

kb_get_units = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,  # make the buttons smaller if there are more than 3
    keyboard=[
        [
            KeyboardButton(text='шт'),
            KeyboardButton(text='кг'),
            KeyboardButton(text='м'),
            KeyboardButton(text='л')
        ]
    ]
)


def get_products(master: dict, products_page: dict, page: int) -> InlineKeyboardMarkup:
    keyboard = get_back()
    permissions = tools.permissions(master)

    #cb_data = {'state': Generic.CALLBACK_TO_MESSAGE_INIT}

    page_row = _get_pages(
        products_page,
        cb.menu_item,
        dict(
            state=Menu.CHOICE,
            action=Menu.PRODUCTS,
            page=page,
        ),
    )

    if ADD in permissions[PRODUCTS]:
        cb_add_data = {
            'state': Generic.CALLBACK_TO_MESSAGE_INIT,
            'action': Product.Create.VENDOR_CODE,
            'data': '',
        }
        keyboard.add(InlineKeyboardButton(
            'Добавить товар', callback_data=cb.generic.new(**cb_add_data)))

    if set([VIEW, EDIT, DELETE]).intersection(permissions[PRODUCTS]):
        cb_edit_data = {
            'state': Product.Edit.MENU,
            'action': Product.Edit.MENU,
        }
        for each in products_page['results']:
            keyboard.add(InlineKeyboardButton(
                each['repr'],
                callback_data=cb.generic.new(
                    data=each['id'], **cb_edit_data
                )))

    if page_row:
        keyboard.row(*page_row)

    return keyboard


def edit_product(master, product):
    keyboard = get_back(PRODUCTS)
    permissions = tools.permissions(master)

    cb_data = {'product_id': product['id']}
    product_id = cb_data['product_id']
    product_id_jsoned = dumps([product_id])


    if EDIT in permissions[PRODUCTS]:
        name_cb = cb.generic.new(
            state=Generic.CALLBACK_TO_MESSAGE_INIT,
            action=Product.Edit.NAME,
            data=product_id_jsoned
        )
        vendor_cb = cb.generic.new(
            state=Generic.CALLBACK_TO_MESSAGE_INIT,
            action=Product.Edit.VENDOR_CODE,
            data=product_id_jsoned
        )
        unit_cb = cb.generic.new(
            state=Generic.CALLBACK_TO_MESSAGE_INIT,
            action=Product.Edit.UNIT,
            data=product_id_jsoned
        )

        keyboard.add(InlineKeyboardButton(
            'Изменить наименование',
            callback_data=name_cb
        ))
        keyboard.add(InlineKeyboardButton(
            'Изменить артикул (код товара)',
            callback_data=vendor_cb
        ))
        keyboard.add(InlineKeyboardButton(
            'Изменить единицы измерения',
            callback_data=unit_cb
        ))
        keyboard.add(InlineKeyboardButton(
            'Изменить категорию',
            callback_data=cb.product_category.new(
                state = Generic.CALLBACK_HANDLE,
                action = Product.Edit.Category.MENU,
                product_id = product_id,
                category_id = '',
                page=1
            )
        ))

    if DELETE in permissions[PRODUCTS]:
        del_cb = cb.generic.new(
            state=Generic.CALLBACK_HANDLE,
            action=Product.Edit.DELETE,
            data=product_id
        )
        keyboard.add(InlineKeyboardButton(
            'Удалить товар',
            callback_data=del_cb
        ))

    return keyboard

def get_product_categories(
    action_class: Product.Create.Category | Product.Edit.Category,
    page,
    product_id,
    categories_page
):
    keyboard = InlineKeyboardMarkup()

    # callback preparation
    cb_data = {
        'state': Generic.CALLBACK_HANDLE,
        'page': page,
        'product_id': product_id}
    
    # for pages row
    page_row = _get_pages(
        categories_page,
        cb.product_category,
        dict(
            action = action_class.MENU,
            category_id='',
            **cb_data))
    
    # add buttons
    for each in categories_page['results']:
        keyboard.add(InlineKeyboardButton(
            each['repr'],
            callback_data=cb.product_category.new(
                action=action_class.SPECIFIC,
                category_id=each['id'],
                **cb_data)))
        
    # insert pages row
    if page_row:
        keyboard.row(*page_row)

    return keyboard 