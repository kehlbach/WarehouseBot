
import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from app.data import callbacks as cb
from app.data.constants import DELETE, EDIT, PROFILES, VIEW
from app.data.states import User
from app.keyboards.menu import get_back
from app.keyboards.user import (btn_add_user, edit_user, get_user_departments,
                                get_user_roles)
from app.loader import bot, db, dp
from app.utils import tools


@dp.callback_query_handler(cb.user_departments.filter(
    action=(
        User.Edit.Departments.MENU,
        User.Create.Departments.MENU,
        User.Edit.Departments.DONE,
        User.Create.Departments.DONE,
        User.Edit.Departments.ALL,
        User.Create.Departments.ALL,
        User.Edit.Departments.SPECIFIC,
        User.Create.Departments.SPECIFIC)),
    state='*')
async def handle_user_edit_department(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    action = callback_data['action']
    page = callback_data.get('page', 1)
    if action in (User.Edit.Departments.MENU, User.Edit.Departments.ALL, User.Edit.Departments.SPECIFIC):
        action_class = User.Edit.Departments
    else:
        action_class = User.Create.Departments

    match callback_data['action']:
        case User.Edit.Departments.ALL | User.Create.Departments.ALL:
            text = 'Choose departments user can work with:'
            profile = db.get(db.PROFILES, callback_data['profile_id'])
            all_departments = db.get(db.DEPARTMENTS)
            all_departments_ids = [i['id'] for i in all_departments]
            departments_page = db.get_page(db.DEPARTMENTS, page)
            if profile['departments'] == all_departments_ids:
                profile = db.edit_put(
                    db.PROFILES,
                    profile,
                    departments=[],
                    requester=callback_query.message.chat.id)
            else:
                profile = db.edit_put(
                    db.PROFILES,
                    profile,
                    departments=all_departments_ids,
                    requester=callback_query.message.chat.id)
            reply_markup = get_user_departments(
                action_class,
                page=page,
                all_departments=all_departments,
                departments_page=departments_page,
                profile=profile
            )
        case User.Create.Departments.MENU | User.Edit.Departments.MENU:
            text = 'Choose departments user can work with:'
            profile = db.get(db.PROFILES, callback_data['profile_id'])
            all_departments = db.get(db.DEPARTMENTS)
            departments_page = db.get_page(db.DEPARTMENTS, page)
            reply_markup = get_user_departments(
                action_class,
                page=page,
                all_departments=all_departments,
                departments_page=departments_page,
                profile=profile
            )
        case User.Edit.Departments.SPECIFIC | User.Create.Departments.SPECIFIC:
            profile = db.get(db.PROFILES, callback_data['profile_id'])
            all_departments = db.get(db.DEPARTMENTS)
            departments_page = db.get_page(db.DEPARTMENTS, page)
            text = 'Choose departments user can work with:'
            profile = db.get(db.PROFILES, callback_data['profile_id'])
            if int(callback_data['department_id']) in profile['departments']:
                profile['departments'].remove(
                    int(callback_data['department_id']))
            else:
                profile['departments'].append(
                    int(callback_data['department_id']))
            profile = db.edit_put(
                db.PROFILES,
                profile,
                requester=callback_query.message.chat.id)
            reply_markup = get_user_departments(
                action_class,
                page=page,
                all_departments=all_departments,
                departments_page=departments_page,
                profile=profile
            )
        case User.Edit.Departments.DONE:
            reply_markup = get_back(PROFILES, callback_data['profile_id'])
            text = 'New departments successfully set.'
        case User.Create.Departments.DONE:
            text = 'User with number {} created'.format(
                callback_data['phone_number'])
            reply_markup = get_back(PROFILES, callback_data['profile_id'])
            reply_markup.add(btn_add_user)

    return await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@dp.callback_query_handler(cb.user_role.filter(
    action=(
        User.Edit.Roles.MENU,
        User.Create.Roles.MENU,
        User.Edit.Roles.SPECIFIC,
        User.Create.Roles.SPECIFIC
    )),
    state='*'
)
async def handle_user_edit_role(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    action = callback_data['action']
    page = callback_data.get('page', 1)

    match action:
        case User.Create.Roles.MENU:
            text = 'Choose user role:'
            roles_page = db.get_page(db.ROLES, page)
            reply_markup = get_user_roles(
                User.Create.Roles, page, callback_data['profile_id'], roles_page)
        case User.Edit.Roles.MENU:
            text = 'Choose user role:'
            roles_page = db.get_page(db.ROLES, page)
            reply_markup = get_user_roles(
                User.Edit.Roles, page, callback_data['profile_id'], roles_page)
        case User.Create.Roles.SPECIFIC:
            text = 'Choose departments user can work with:'
            created_user = db.edit_patch(
                db.PROFILES,
                id=callback_data['profile_id'],
                role=callback_data['role_id'],
                requester=callback_query.message.chat.id)
            all_departments = db.get(db.DEPARTMENTS)
            departments_page = db.get_page(db.DEPARTMENTS, page)
            reply_markup = get_user_departments(
                User.Create.Departments,
                page=page,
                all_departments=all_departments,
                departments_page=departments_page,
                profile=created_user)
        case User.Edit.Roles.SPECIFIC:
            changed_user = db.edit_patch(
                db.PROFILES,
                id=callback_data['profile_id'],
                role=callback_data['role_id'],
                requester=callback_query.message.chat.id)
            text = 'Role successfully changed. New role - {}.'.format(
                changed_user['role_name'])
            reply_markup = get_back(PROFILES, callback_data['profile_id'])

    return await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@dp.callback_query_handler(cb.generic.filter(action=(User.Edit.DELETE)), state='*')
async def handle_user_delete(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    profile_id = callback_data['data']
    response = db.delete(
        db.PROFILES,
        id=profile_id,
        requester=callback_query.message.chat.id,
        raise_error=False)
    if response.status_code == 204:
        text = 'User deleted successfully.'
    elif response.status_code == 403:
        text = 'No permission to delete user.'
    else:
        text = 'An error occurred while deleting the user.'
        logging.warning('⭕User was not deleted')
    reply_markup = get_back(PROFILES)
    return await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@dp.callback_query_handler(cb.generic.filter(state=User.Edit.MENU), state='*')
async def edit_user_init(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    master_user_id = callback_query.from_user.id
    master = db.filter(db.PROFILES, user_id=master_user_id)
    profile_id = callback_data['data']
    permissions = tools.permissions(master)
    if set([VIEW, EDIT, DELETE]).intersection(permissions[PROFILES]):
        profile = db.get(db.PROFILES, profile_id)
        all_departments = db.get(db.DEPARTMENTS)
        if master['id'] == profile['id']:
            text = 'This is you'
        else:
            text = 'User'
        all_departments_id_to_name = {
            i['id']: i['name'] for i in all_departments}
        if profile['departments'] == list(all_departments_id_to_name.keys()):
            user_department_names = 'all departments'
        else:
            user_department_names = '\n'.join(
                [all_departments_id_to_name[i] for i in profile['departments']])
        text += '\nName: ' + profile['name'] +\
                '\nPhone number: ' + profile['phone_number'] +\
                '\nRole: ' + profile['role_name'] +\
                '\nDepartments: '+user_department_names
        reply_markup = edit_user(master=master,
                                 profile=profile)
        return await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text=text,
            reply_markup=reply_markup
        )
    else:
        return await callback_query.answer('No access')
