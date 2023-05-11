from app.data import callbacks as cb
from app.data.constants import ADD, DELETE, EDIT, ROLES, VIEW
from app.data.constants.actions import ALL_ACTIONS
from app.data.constants.subjects import ALL_SUBJECTS
from app.data.states import Generic, Menu, Role
from app.keyboards.menu import _get_pages, get_back
from app.utils import tools


from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


from copy import deepcopy
from json import dumps, loads


def get_roles(master: dict, roles_page: dict, page: int) -> InlineKeyboardMarkup:
    keyboard = get_back()
    permissions = tools.permissions(master)

    cb_data = {
        'state': Generic.CALLBACK_TO_MESSAGE_INIT,
    }

    page_row = _get_pages(
        roles_page,
        cb.menu_item,
        dict(
            state=Menu.CHOICE,
            action=Menu.ROLES,
            page=page))


    if ADD in permissions[ROLES]:
        cb_add_data = {
            'state': Generic.CALLBACK_TO_MESSAGE_INIT,
            'action': Role.Create.NAME,
            'data': ''
        }
        keyboard.add(InlineKeyboardButton(
            'Добавить роль', callback_data=cb.generic.new(**cb_add_data)))
    if set([VIEW, EDIT, DELETE]).intersection(permissions[ROLES]):
        cb_edit_data = {
            'state': Role.Edit.MENU,
            'action': Role.Edit.MENU}
        for each in roles_page['results']:
            keyboard.add(InlineKeyboardButton(
                each['repr'],
                callback_data=cb.generic.new(
                    data=each['id'], **cb_edit_data
                )))

    if page_row:
        keyboard.row(*page_row)

    return keyboard


def edit_role(master, role):
    keyboard = get_back(ROLES)
    permissions = tools.permissions(master)

    cb_data = {'role_id': role['id']}

    if EDIT in permissions[ROLES]:
        keyboard.add(InlineKeyboardButton(
            'Изменить название',
            callback_data=cb.generic.new(
                state=Generic.CALLBACK_TO_MESSAGE_INIT,
                action=Role.Edit.NAME,
                data=dumps(
                    [cb_data['role_id']],
                )
            )
        ))
        keyboard.add(InlineKeyboardButton(
            'Изменить разрешения',
            callback_data=cb.role_permissions.new(
                state=Role.Edit.Permissions.MENU,
                action=Role.Edit.Permissions.MENU,
                subject_id = '',
                action_id = '',
                role_id = cb_data['role_id'],
                )
            )
        )

    if DELETE in permissions[ROLES]:
        keyboard.add(InlineKeyboardButton(
            'Удалить роль',
            callback_data=cb.generic.new(
                state=Generic.CALLBACK_HANDLE,
                action=Role.Edit.DELETE,
                data=cb_data['role_id'])))
    return keyboard


def get_role_permissions(
        action_class: Role.Edit.Permissions | Role.Create.Permissions,
        role):
    keyboard = InlineKeyboardMarkup()


    # callback preparation
    cb_data = {
        'state': '',
        # 'action': action,
        'role_id': role['id']
    }
    # pages preparation


    keyboard.add(InlineKeyboardButton(
        'Готово',
        callback_data=cb.role_permissions.new(
            action=action_class.DONE,
            subject_id = '',
            action_id='',
            **cb_data)))
    permissions = dict(loads(role['permissions']))

    for subject_id, subject_name in ALL_SUBJECTS.items():
        if permissions[subject_id] == list(ALL_ACTIONS.keys()):
            checked = '✅ '
        elif permissions[subject_id]:
            checked = '🟡 '
        else:
            checked = '❌ '
        keyboard.add(InlineKeyboardButton(
            checked+subject_name,
            callback_data=cb.role_permissions.new(
                action=action_class.SUBJECT,
                subject_id=subject_id,
                action_id='',
                **cb_data
            )
        ))
    return keyboard

def get_role_permission(action_class: Role.Edit.Permissions | Role.Create.Permissions,
                    role,
                    subject_id):
    keyboard = InlineKeyboardMarkup()

    cb_data = {
        'state': '',
        # 'action': action,
        'role_id': role['id']
    }
    # pages preparation

    keyboard.add(InlineKeyboardButton(
        'Назад',
        callback_data=cb.role_permissions.new(
            action=action_class.BACK,
            subject_id='',
            action_id='',
            **cb_data
        )))
    permissions = dict(loads(role['permissions']))
    keyboard

    if permissions[subject_id] == list(ALL_ACTIONS.keys()):
        checked = '✅ '
    else:
        checked = '❌ '
    keyboard.add(InlineKeyboardButton(
            checked+'Все разрешения',
            callback_data=cb.role_permissions.new(
                action=action_class.ALL,
                subject_id=subject_id,
                action_id='',
                **cb_data
            )
        ))

    for action_id, action_name in ALL_ACTIONS.items():
        if action_id in permissions[subject_id]:
            checked = '✅ '
        else:
            checked = '❌ '
        keyboard.add(InlineKeyboardButton(
            checked+action_name.capitalize(),
            callback_data=cb.role_permissions.new(
                action=action_class.SPECIFIC,
                subject_id=subject_id,
                action_id=action_id,
                **cb_data
            )
        ))
    
    return keyboard
