from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import BadRequest

from app.data import callbacks as cb
from app.data.constants import (
    CATEGORIES,
    DEPARTMENTS,
    INVENTORY,
    PRODUCTS,
    PROFILES,
    RECEIPTS,
    ROLES,
)
from app.data.states import CURRENT_PAGE, Login, Menu
from app.keyboards.category import get_categories
from app.keyboards.department import get_departments
from app.keyboards.inventory import get_inventory_department
from app.keyboards.product import get_products
from app.keyboards.receipt import get_receipt_department
from app.keyboards.role import get_roles
from app.keyboards.user import get_profiles
from app.loader import bot, db, dp
from app.utils import tools

from .login import _prepare_menu


@dp.callback_query_handler(cb.action.filter(action=Menu.INIT), state="*")
@dp.callback_query_handler(cb.action.filter(action=Login.CHECK), state="*")
async def process_menu_init(
    callback_query: CallbackQuery, callback_data: dict, state: FSMContext
):
    user_id = callback_query["from"]["id"]
    master = db.filter(db.PROFILES, user_id=user_id)
    try:
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            **_prepare_menu(master),
        )
    except BadRequest:
        try:
            await bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
            )
        finally:
            await bot.send_message(
                chat_id=callback_query.message.chat.id, **_prepare_menu(master)
            )


@dp.callback_query_handler(cb.menu_item.filter(state=Menu.CHOICE), state="*")
async def process_menu_choice(
    callback_query: CallbackQuery, callback_data: dict, state: FSMContext
):
    user_id = callback_query["from"]["id"]
    master = db.filter(db.PROFILES, user_id=user_id)
    permissions = tools.permissions(master)
    match callback_data["action"]:
        case Menu.PROFILES:
            if not permissions[PROFILES]:
                raise PermissionError
            profiles_page = db.get_page(db.PROFILES, callback_data.get("page", 1))
            text = "Select user"
            reply_markup = get_profiles(
                master, profiles_page, callback_data.get("page", 1)
            )
        case Menu.ROLES:
            if not permissions[ROLES]:
                raise PermissionError
            roles_page = db.get_page(db.ROLES, callback_data.get("page", 1))
            text = "Select role"
            reply_markup = get_roles(master, roles_page, callback_data.get("page", 1))
        case Menu.INVENTORY:
            if not permissions[INVENTORY]:
                raise PermissionError
            departments_page = db.get_page(db.DEPARTMENTS, callback_data.get("page", 1))
            text = "Select department to view inventory"
            reply_markup = get_inventory_department(
                master, departments_page, callback_data.get("page", 1)
            )
            try:
                return await bot.edit_message_text(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.message_id,
                    text=text,
                    reply_markup=reply_markup,
                )
            except:
                try:
                    await bot.delete_message(
                        chat_id=callback_query.message.chat.id,
                        message_id=callback_query.message.message_id,
                    )
                finally:
                    return await bot.send_message(
                        chat_id=callback_query.message.chat.id,
                        text=text,
                        reply_markup=reply_markup,
                    )
        case Menu.RECEIPTS:
            if not permissions[RECEIPTS]:
                raise PermissionError
            departments_page = db.get_page(db.DEPARTMENTS, callback_data.get("page", 1))
            text = "Select department to view receipts"
            reply_markup = get_receipt_department(
                master, departments_page, callback_data.get("page", 1)
            )
        case Menu.PRODUCTS:
            if not permissions[PRODUCTS]:
                raise PermissionError
            products_page = db.get_page(db.PRODUCTS, callback_data.get("page", 1))
            text = "Select product"
            reply_markup = get_products(
                master, products_page, callback_data.get("page", 1)
            )
        case Menu.CATEGORIES:
            if not permissions[CATEGORIES]:
                raise PermissionError
            categories_page = db.get_page(db.CATEGORIES, callback_data.get("page", 1))
            text = "Select category"
            reply_markup = get_categories(
                master, categories_page, callback_data.get("page", 1)
            )
        case Menu.DEPARTMENTS:
            if not permissions[DEPARTMENTS]:
                raise PermissionError
            departments_page = db.get_page(db.DEPARTMENTS, callback_data.get("page", 1))
            text = "Select department"
            reply_markup = get_departments(
                master, departments_page, callback_data.get("page", 1)
            )
    try:
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text=text,
            reply_markup=reply_markup,
        )
    except:
        try:
            await bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
            )
        finally:
            return await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text=text,
                reply_markup=reply_markup,
            )


@dp.callback_query_handler(cb.menu_item.filter(state=CURRENT_PAGE), state="*")
async def process_current_page(
    callback_query: CallbackQuery, callback_data: dict, state: FSMContext
):
    page = callback_data["page"]
    await callback_query.answer("page {}.".format(page))
