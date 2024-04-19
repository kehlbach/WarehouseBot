
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.data import callbacks as cb
from app.data.constants import DELETE, EDIT, INVENTORY, VIEW
from app.data.states import Inventory, Menu
from app.keyboards.menu import _get_pages, get_back
from app.utils import tools


def get_inventory_department(master: dict, departments_page: dict, page: int) -> InlineKeyboardMarkup:
    keyboard = get_back()
    permissions = tools.permissions(master)

    page_row = _get_pages(
        departments_page,
        cb.menu_item,
        dict(
            state=Menu.CHOICE,
            action=Menu.INVENTORY,
            page=page,
        ),
    )

    if set([VIEW, EDIT, DELETE]).intersection(permissions[INVENTORY]):
        cb_edit_data = {
            'state': Inventory.View.DEPARTMENT,
            'action': Inventory.View.DEPARTMENT,
        }
        keyboard.add(InlineKeyboardButton(
            'All available departments',
            callback_data=cb.generic.new(
                data='', **cb_edit_data
            )))
        for each in departments_page['results']:
            if each['id'] in master['departments'] and not (each['is_hidden']):
                keyboard.add(InlineKeyboardButton(
                    each['repr'],
                    callback_data=cb.generic.new(
                        data=each['id'], **cb_edit_data
                    )))

    if page_row:
        keyboard.row(*page_row)

    return keyboard


def kb_view_inventory(master, department):
    keyboard = get_back(INVENTORY)
    permissions = tools.permissions(master)
    cb_data = {
        'state': Inventory.View.BY_DATE,
        'action': Inventory.View.BY_DATE,
    }
    keyboard.add(InlineKeyboardButton(
        'By date', callback_data=cb.generic.new(
            state=Inventory.View.BY_DATE,
            action=Inventory.View.BY_DATE,
            data=department
        )
    ))

    return keyboard
