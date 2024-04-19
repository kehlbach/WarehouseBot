import re

from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

from app.data import callbacks as cb
from app.data.constants import *
from app.data.states import *
from app.utils import tools

kb_check_status = InlineKeyboardMarkup()
kb_check_status.add(InlineKeyboardButton('Проверить статус', callback_data=cb.action.new(action=Login.CHECK)))


def get_back(subject='', data=''):
    """if user_id provided then back to user available
    Buttons:
        - В меню
        - К списку пользователей
        - К пользователю
    """
    match subject:
        case subjects.PROFILES:
            to_first_menu_text = 'К списку пользователей'
            to_first_menu_action = Menu.PROFILES
            subject_text = 'К пользователю'
            subject_action = User.Edit.MENU
        case subjects.ROLES:
            to_first_menu_text = 'К списку ролей'
            to_first_menu_action = Menu.ROLES
            subject_text = 'К роли'
            subject_action = Role.Edit.MENU
        case subjects.INVENTORY:
            to_first_menu_text = 'К выбору отделения'
            to_first_menu_action = Menu.INVENTORY
            #subject_text = ['К списку накладных']
            #subject_action = [Inventory.View.DEPARTMENT]
        case subjects.RECEIPTS:
            to_first_menu_text = 'К выбору отделения'
            to_first_menu_action = Menu.RECEIPTS
            subject_text = ['К списку накладных',
                            'К накладной']
            subject_action = [Receipt.Edit.DEPARTMENT,
                              Receipt.Edit.MENU]
        case subjects.PRODUCTS:
            to_first_menu_text = 'К списку товаров'
            to_first_menu_action = Menu.PRODUCTS
            subject_text = 'К товару'
            subject_action = Product.Edit.MENU
        case subjects.CATEGORIES:
            to_first_menu_text = 'К списку категорий'
            to_first_menu_action = Menu.CATEGORIES
            subject_text = 'К категории'
            subject_action = Category.Edit.MENU
        case subjects.DEPARTMENTS:
            to_first_menu_text = 'К списку отделений'
            to_first_menu_action = Menu.DEPARTMENTS
            subject_text = 'К отделению'
            subject_action = Department.Edit.MENU

    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(
        'В меню', callback_data=cb.action.new(action=Menu.INIT)))
    if subject:
        keyboard.add(InlineKeyboardButton(
            to_first_menu_text,
            callback_data=cb.menu_item.new(
                state=Menu.CHOICE,
                action=to_first_menu_action,
                page=1)))
        if data:
            if type(data) == list:
                for each in range(len(data)):
                    keyboard.add(InlineKeyboardButton(
                        subject_text[each],
                        callback_data=cb.generic.new(
                            state=subject_action[each],
                            action=subject_action[each],
                            data=data[each])))
            else:
                keyboard.add(InlineKeyboardButton(
                    subject_text,
                    callback_data=cb.generic.new(
                        state=subject_action,
                        action=subject_action,
                        data=data)))
    return keyboard


kb_send_number = ReplyKeyboardMarkup(
    resize_keyboard=True, selective=True, one_time_keyboard=True)
kb_send_number.add(KeyboardButton(
    text="Отправить телефон", request_contact=True))
kb_skip = ReplyKeyboardMarkup(
    resize_keyboard=True, selective=True, one_time_keyboard=True)
kb_skip.add(KeyboardButton(
    text="Пропустить"))


KB_MAIN_MENU = '1'
KB_SUBJECT_ENTITIES = '2'
KB_USER_ROLES = '3'
KB_USER_DEPARTMENTS = '4'
KB_EDIT_USER = '5'
DONE = 'D'


def _get_pages(response, cb_type, cb_data):
    page_row = []

    if response['previous'] or response['next']:
        if response['previous']:
            prev_page = re.search(r'page=(\d+)', response['previous'])
            if prev_page:
                prev_page = prev_page.group(1)
            else:
                prev_page = 1
            cb_data['page'] = prev_page
            page_row.append(InlineKeyboardButton(
                '<', callback_data=cb_type.new(**cb_data)),)
        if response['next']:
            next_page = re.search(r'page=(\d+)', response['next']).group(1)
            cb_data['page'] = next_page
            cur_page_data = {
                'state': CURRENT_PAGE,
                'action': '',
                'page': int(next_page)-1
            }
            page_row.append(InlineKeyboardButton(
                str(int(next_page)-1), callback_data=cb.menu_item.new(**cur_page_data)),)
            page_row.append(InlineKeyboardButton(
                '>', callback_data=cb_type.new(**cb_data)),)
        else:
            cur_page_data = {
                'state': CURRENT_PAGE,
                'action': '',
                'page': int(prev_page)+1
            }
            page_row.append(InlineKeyboardButton(
                str(int(prev_page)+1), callback_data=cb.menu_item.new(**cur_page_data)),)
    return page_row


def get_main_menu(master):
    keyboard = InlineKeyboardMarkup()
    permissions = tools.permissions(master)
    get_menu_action = {
        PROFILES: Menu.PROFILES,
        ROLES: Menu.ROLES,
        INVENTORY: Menu.INVENTORY,
        RECEIPTS: Menu.RECEIPTS,
        PRODUCTS: Menu.PRODUCTS,
        CATEGORIES: Menu.CATEGORIES,
        DEPARTMENTS: Menu.DEPARTMENTS
    }

    cb_data = {
        'state': Menu.CHOICE,
        'page': 1
    }

    permissions = tools.permissions(master)
    for subject in ALL_SUBJECTS.keys():
        if permissions[subject]:
            keyboard.add(InlineKeyboardButton(
                ALL_SUBJECTS[subject], callback_data=cb.menu_item.new(action=get_menu_action[subject], **cb_data)))

    return keyboard
