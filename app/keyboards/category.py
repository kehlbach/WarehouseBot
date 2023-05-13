from json import dumps

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.data import callbacks as cb
from app.data.constants import *
from app.data.constants import ADD, CATEGORIES, DELETE, EDIT, VIEW
from app.data.states import *
from app.data.states import Category, Generic, Menu
from app.keyboards.menu import _get_pages, get_back
from app.utils import tools


def edit_category(master, category):
    keyboard = get_back(CATEGORIES)
    permissions = tools.permissions(master)
    cb_data = {'category_id': category['id']}
    if EDIT in permissions[CATEGORIES]:
        keyboard.add(InlineKeyboardButton(
            'Изменить название',
            callback_data=cb.generic.new(
                state=Generic.CALLBACK_TO_MESSAGE_INIT,
                action=Category.Edit.NAME,
                data=dumps([cb_data['category_id']],)
            )
        ))
    if DELETE in permissions[PROFILES]:
        keyboard.add(InlineKeyboardButton(
            'Удалить категорию',
            callback_data=cb.generic.new(
                state=Generic.CALLBACK_HANDLE,
                action=Category.Edit.DELETE,
                data=cb_data['category_id'])))
    return keyboard


def get_categories(master: dict, categories_page: dict, page: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    permissions = tools.permissions(master)
    page_row = _get_pages(
        categories_page,
        cb.menu_item,
        dict(
            state=Menu.CHOICE,
            action=Menu.CATEGORIES,
            page=page))
    keyboard.add(InlineKeyboardButton(
        'В меню', callback_data=cb.action.new(action=Menu.INIT)))
    if ADD in permissions[CATEGORIES]:
        cb_add_data = {
            'state': Generic.CALLBACK_TO_MESSAGE_INIT,
            'action': Category.Create.NAME,
            'data': ''
        }
        keyboard.add(InlineKeyboardButton(
            'Добавить категорию', callback_data=cb.generic.new(**cb_add_data)))
    if set([VIEW, EDIT, DELETE]).intersection(permissions[CATEGORIES]):
        cb_edit_data = {
            'state': Category.Edit.MENU,
            'action': Category.Edit.MENU}
        for each in categories_page['results']:
            keyboard.add(InlineKeyboardButton(
                each['repr'],
                callback_data=cb.generic.new(data=each['id'], **cb_edit_data)))
    if page_row:
        keyboard.row(*page_row)
    return keyboard
