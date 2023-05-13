from json import dumps

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.data import callbacks as cb
from app.data.constants import ADD, DELETE, EDIT, PROFILES, VIEW
from app.data.states import Generic, Menu, User
from app.keyboards.menu import _get_pages, get_back
from app.utils import tools

btn_add_user = InlineKeyboardButton(
    'Добавить пользователя', callback_data=cb.generic.new(
        state= Generic.CALLBACK_TO_MESSAGE_INIT,
        action= User.Create.NUMBER,
        data= ''))

def edit_user(master: dict, profile: dict) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard with available (according to permissions) options to change profiles.
    Buttons:
        - В меню
        - К списку пользователей
        - Изменить имя
        - Изменить номер
        - Изменить роль
        - Изменить отделения
        - Удалить пользователя

    Args:
        master (dict): The user requesting keyboard.
        profile (dict): The user's profile to be edited.

    Returns:
        InlineKeyboardMarkup: The inline keyboard with edit options.
    """

    keyboard = get_back(PROFILES)
    permissions = tools.permissions(master)

    cb_data = {'profile_id': profile['id']}

    if EDIT in permissions[PROFILES]:
        keyboard.add(InlineKeyboardButton(
            'Изменить имя',
            callback_data=cb.generic.new(
                state=Generic.CALLBACK_TO_MESSAGE_INIT,
                action=User.Edit.NAME,
                data=dumps([cb_data['profile_id']]))))
        if master['id'] == profile['id']:
            keyboard.add(InlineKeyboardButton(
                'Изменить номер',
                callback_data=cb.generic.new(
                    state=Generic.CALLBACK_TO_MESSAGE_INIT,
                    action=User.Edit.NUMBER_OWN,
                    data=dumps(
                        [cb_data['profile_id'],
                         profile['phone_number']]))))
        else:
            keyboard.add(InlineKeyboardButton(
                'Изменить номер',
                callback_data=cb.generic.new(
                    state=Generic.CALLBACK_TO_MESSAGE_INIT,
                    action=User.Edit.NUMBER,
                    data=dumps(
                        [cb_data['profile_id'],
                         profile['phone_number']]))))
            keyboard.add(InlineKeyboardButton(
                'Изменить роль',
                callback_data=cb.user_role.new(
                    state=Generic.CALLBACK_HANDLE,
                    action=User.Edit.Roles.MENU,
                    role_id='',
                    page=1,
                    **cb_data)))
        keyboard.add(InlineKeyboardButton(
            'Изменить отделения',
            callback_data=cb.user_departments.new(
                state=Generic.CALLBACK_HANDLE,
                action=User.Edit.Departments.MENU,
                department_id='',
                phone_number='',
                page=1,
                **cb_data)))
    if DELETE in permissions[PROFILES] and not master['id'] == profile['id']:
        keyboard.add(InlineKeyboardButton(
            'Удалить пользователя',
            callback_data=cb.generic.new(
                state=Generic.CALLBACK_HANDLE,
                action=User.Edit.DELETE,
                data=cb_data['profile_id'])))

    return keyboard


def get_user_departments(
        action_class: User.Create.Departments | User.Edit.Departments,
        page,
        all_departments,
        departments_page,
        profile):
    keyboard = InlineKeyboardMarkup()

    cb_data = {
        'state': '',
        'page': page,
        'profile_id': profile['id']
    }

    page_row = _get_pages(
        departments_page,
        cb.user_departments,
        dict(
            action=action_class.MENU,
            department_id='',
            phone_number='',
            **cb_data))

    keyboard.add(InlineKeyboardButton(
        'Готово',
        callback_data=cb.user_departments.new(
            action=action_class.DONE,
            phone_number=profile['phone_number'],
            department_id='',
            **cb_data)))
    if profile['departments'] == [i['id'] for i in all_departments]:
        checked_1 = '✅ '
    else:
        checked_1 = '❌ '
    keyboard.add(InlineKeyboardButton(
        checked_1+'Все отделения',
        callback_data=cb.user_departments.new(
            action=action_class.ALL,
            department_id='',
            phone_number='',
            **cb_data)))
    for each in departments_page['results']:
        if each['id'] in profile['departments']:
            checked_2 = '✅ '
        else:
            checked_2 = '❌ '
        keyboard.add(InlineKeyboardButton(
            checked_2+each['repr'],
            callback_data=cb.user_departments.new(
                action=action_class.SPECIFIC,
                department_id=each['id'],
                phone_number='',
                **cb_data)))
    if page_row:
        keyboard.row(*page_row)
    return keyboard


def get_user_roles(
        action_class: User.Create.Roles | User.Edit.Roles,
        page,
        profile_id,
        roles_page):
    keyboard = InlineKeyboardMarkup()

    cb_data = {
        'state': Generic.CALLBACK_HANDLE,
        'page': page,
        'profile_id': profile_id
    }

    page_row = _get_pages(
        roles_page,
        cb.user_role,
        dict(
            action=action_class.MENU,
            role_id='',
            **cb_data))

    for each in roles_page['results']:
        keyboard.add(InlineKeyboardButton(
            each['repr'],
            callback_data=cb.user_role.new(
                action=action_class.SPECIFIC,
                role_id=each['id'],
                **cb_data)))

    if page_row:
        keyboard.row(*page_row)

    return keyboard




def get_profiles(master: dict, profiles_page: dict, page: int):
    keyboard = InlineKeyboardMarkup()
    permissions = tools.permissions(master)

    page_row = _get_pages(
        profiles_page,
        cb.menu_item,
        dict(
            state=Menu.CHOICE,
            action=Menu.PROFILES,
            page=page))
    keyboard.add(InlineKeyboardButton(
        'В меню', callback_data=cb.action.new(action=Menu.INIT)))

    if ADD in permissions[PROFILES]:
        keyboard.add(btn_add_user)

    # checks if user has any permission from set about PROFILES
    if set([VIEW, EDIT, DELETE]).intersection(permissions[PROFILES]):
        cb_edit_data = {
            'state': User.Edit.MENU,
            'action': User.Edit.MENU}
        for each in profiles_page['results']:
            keyboard.add(InlineKeyboardButton(
                each['repr'],
                callback_data=cb.generic.new(
                    data=each['id'], **cb_edit_data
                )))

    if page_row:
        keyboard.row(*page_row)

    return keyboard

