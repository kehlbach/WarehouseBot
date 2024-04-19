
import logging
from json import loads

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from app.data import callbacks as cb
from app.data.constants import (ALL_ACTIONS, ALL_SUBJECTS, DELETE, EDIT, ROLES,
                                VIEW)
from app.data.states import Role
from app.keyboards.menu import get_back
from app.keyboards.role import (edit_role, get_role_permission,
                                get_role_permissions)
from app.loader import bot, db, dp
from app.utils import tools


@dp.callback_query_handler(cb.generic.filter(state=Role.Edit.MENU), state='*')
async def edit_role_init(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    master_user_id = callback_query.from_user.id
    master = db.filter(db.PROFILES, user_id=master_user_id)
    permissions = tools.permissions(master)
    role_id = callback_data['data']
    if set([VIEW, EDIT, DELETE]).intersection(permissions[ROLES]):
        role = db.get(db.ROLES, role_id)
        permissions_text = role['permissions_repr']
        replaces = {' ': '\n    ', ',': ', ', ':': ': ',
                    'view, add, edit, delete': 'full access'}
        for key, value in replaces.items():
            permissions_text = permissions_text.replace(key, value)
        text = 'Role: ' + role['name']+'\nPermissions: \n    '+permissions_text
        reply_markup = edit_role(master, role=role,)
    else:
        text = 'No access'
        reply_markup = None
    return await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@dp.callback_query_handler(cb.role_permissions.filter(
    action=(
        Role.Edit.Permissions.MENU,
        Role.Edit.Permissions.DONE,
        Role.Edit.Permissions.ALL,
        Role.Edit.Permissions.SPECIFIC,
        Role.Edit.Permissions.SUBJECT,
        Role.Create.Permissions.MENU,
        Role.Create.Permissions.DONE,
        Role.Create.Permissions.ALL,
        Role.Create.Permissions.SPECIFIC,
        Role.Create.Permissions.SUBJECT,
        Role.Create.Permissions.BACK,
        Role.Edit.Permissions.BACK)),
    state='*')
async def init_role_permissions(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    master_user_id = callback_query.from_user.id
    master = db.filter(db.PROFILES, user_id=master_user_id)
    action = callback_data['action']
    permissions = tools.permissions(master)
    role_id = int(callback_data['role_id'])
    permissions_class = Role.Edit.Permissions
    permissions_field_values = [
        getattr(permissions_class, attr) for attr in dir(permissions_class)]
    if action in permissions_field_values:
        action_class = Role.Edit.Permissions
    else:
        action_class = Role.Create.Permissions
    if action == action_class.BACK:
        text = 'Select entity:'
        role = db.get(db.ROLES, role_id)
        reply_markup = get_role_permissions(action_class, role)
    elif action == action_class.DONE:
        if action_class == Role.Create.Permissions:
            text = 'Role created.'
        else:
            text = 'Role permissions editing completed.'
        reply_markup = get_back(ROLES, role_id)
    else:
        if EDIT in permissions[ROLES] and not role_id == master['role']:
            match action:
                case action_class.MENU:
                    role = db.get(db.ROLES, role_id)
                    text = 'Select role:'
                    reply_markup = get_role_permissions(action_class, role)
                case action_class.ALL:
                    subject_id = int(callback_data['subject_id'])
                    text = 'Select permissions for role "{}":'.format(
                        ALL_SUBJECTS[subject_id])
                    role = db.get(db.ROLES, role_id)
                    permissions = dict(loads(role['permissions']))
                    if permissions[subject_id] == list(ALL_ACTIONS.keys()):
                        role_permissions = db.filter(
                            db.ROLE_PERMISSIONS, role=role_id, subject=subject_id)
                        for each in role_permissions:
                            db.delete(
                                db.ROLE_PERMISSIONS, each['id'], requester=callback_query.message.chat.id)
                    elif permissions[subject_id] == []:
                        for each in ALL_ACTIONS.keys():
                            db.add(db.ROLE_PERMISSIONS, role=role_id, subject=subject_id,
                                   action=each, requester=callback_query.message.chat.id)
                    else:
                        absent_rights = set(
                            ALL_ACTIONS.keys()) - set(permissions[subject_id])
                        for each in absent_rights:
                            db.add(db.ROLE_PERMISSIONS, role=role_id, subject=subject_id,
                                   action=each, requester=callback_query.message.chat.id)
                    role = db.get(db.ROLES, role_id)
                    reply_markup = get_role_permission(
                        action_class, role, subject_id)
                case action_class.SUBJECT:
                    role = db.get(db.ROLES, role_id)
                    subject_id = int(callback_data['subject_id'])
                    text = 'Select permissions for role "{}":'.format(
                        ALL_SUBJECTS[subject_id])
                    reply_markup = get_role_permission(
                        action_class, role, subject_id)
                case action_class.SPECIFIC:
                    subject_id = int(callback_data['subject_id'])
                    action_id = int(callback_data['action_id'])
                    role = db.get(db.ROLES, role_id)
                    permissions = permissions = dict(
                        loads(role['permissions']))
                    text = 'Select permissions for role "{}":'.format(
                        ALL_SUBJECTS[subject_id])
                    if action_id in permissions[subject_id]:
                        role_permission = db.filter(db.ROLE_PERMISSIONS, role=role_id,
                                                    subject=subject_id, action=action_id)
                        db.delete(
                            db.ROLE_PERMISSIONS, role_permission['id'], requester=callback_query.message.chat.id)
                    else:
                        db.add(db.ROLE_PERMISSIONS, role=role_id, subject=subject_id,
                               action=action_id, requester=callback_query.message.chat.id)
                    role = db.get(db.ROLES, role_id)
                    reply_markup = get_role_permission(
                        action_class, role, subject_id)

        elif role_id == master['role']:
            return await callback_query.answer('Unable to change permissions for your role.')
        else:
            return await callback_query.answer('Not enough permissions.')
    return await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@dp.callback_query_handler(cb.generic.filter(action=(Role.Edit.DELETE)), state='*')
async def handle_role_delete(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    role_id = callback_data['data']
    response = db.delete(
        db.ROLES,
        id=role_id,
        requester=callback_query.message.chat.id,
        raise_error=False)
    reply_markup = get_back(ROLES)
    if response.status_code == 204:
        text = 'Role successfully deleted.'
    elif response.status_code == 403:
        text = 'Insufficient permissions to delete role.'
    elif 'ProtectedError' in response.text:
        reply_markup = get_back(ROLES, data=role_id)
        text = 'Cannot delete role that has assigned users.'
    else:
        text = 'An error occurred while deleting role.'
        logging.warning('⭕ role not deleted')

    return await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )
