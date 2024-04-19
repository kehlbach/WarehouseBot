from json import dumps

from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

from app.data import callbacks as cb
from app.data.constants import *
from app.data.constants import ADD, DELETE, EDIT, VIEW
from app.data.states import *
from app.data.states import Department, Generic, Menu
from app.keyboards.menu import _get_pages, get_back
from app.utils import tools

edit_department_location = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
edit_department_location.add(KeyboardButton('Remove location'))


def edit_department(master, department):
    keyboard = get_back(DEPARTMENTS)
    permissions = tools.permissions(master)
    cb_data = {'department_id': department['id']}
    if EDIT in permissions[DEPARTMENTS]:
        keyboard.add(InlineKeyboardButton(
            'Rename',
            callback_data=cb.generic.new(
                state=Generic.CALLBACK_TO_MESSAGE_INIT,
                action=Department.Edit.NAME,
                data=dumps([cb_data['department_id']],)
            )
        ))
        keyboard.add(InlineKeyboardButton(
            'Change location',
            callback_data=cb.generic.new(
                state=Generic.CALLBACK_TO_MESSAGE_INIT,
                action=Department.Edit.LOCATION,
                data=dumps([cb_data['department_id']],)
            )
        ))
    if DELETE in permissions[DEPARTMENTS]:
        keyboard.add(InlineKeyboardButton(
            'Delete department',
            callback_data=cb.generic.new(
                state=Generic.CALLBACK_HANDLE,
                action=Department.Edit.DELETE,
                data=cb_data['department_id'])))
    return keyboard


def get_departments(master: dict, departments_page: dict, page: int) -> InlineKeyboardMarkup:
    keyboard = get_back()
    permissions = tools.permissions(master)

    page_row = _get_pages(
        departments_page,
        cb.menu_item,
        dict(
            state=Menu.CHOICE,
            action=Menu.DEPARTMENTS,
            page=page))

    if ADD in permissions[DEPARTMENTS]:
        cb_add_data = {
            'state': Generic.CALLBACK_TO_MESSAGE_INIT,
            'action': Department.Create.NAME,
            'data': ''
        }
        keyboard.add(InlineKeyboardButton(
            'Add department', callback_data=cb.generic.new(**cb_add_data)))
    if set([VIEW, EDIT, DELETE]).intersection(permissions[DEPARTMENTS]):
        cb_edit_data = {
            'state': Department.Edit.MENU,
            'action': Department.Edit.MENU}
        for each in departments_page['results']:
            keyboard.add(InlineKeyboardButton(
                each['repr'],
                callback_data=cb.generic.new(data=each['id'], **cb_edit_data)
            )
            )
    if page_row:
        keyboard.row(*page_row)
    return keyboard
