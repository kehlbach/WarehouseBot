import re

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.data import callbacks as cb
from app.data.constants import (
    ALL_SUBJECTS,
    CATEGORIES,
    DEPARTMENTS,
    INVENTORY,
    PRODUCTS,
    PROFILES,
    RECEIPTS,
    ROLES,
    subjects,
)
from app.data.states import (
    CURRENT_PAGE,
    Category,
    Department,
    Login,
    Menu,
    Product,
    Receipt,
    Role,
    User,
)
from app.utils import tools

kb_check_status = InlineKeyboardMarkup()
kb_check_status.add(
    InlineKeyboardButton(
        "Check status", callback_data=cb.action.new(action=Login.CHECK)
    )
)


def get_back(subject="", data=""):
    """if user_id provided then back to user available
    Buttons:
        - Back to menu
        - To list of users
        - To user
    """
    match subject:
        case subjects.PROFILES:
            to_first_menu_text = "To list of users"
            to_first_menu_action = Menu.PROFILES
            subject_text = "To user"
            subject_action = User.Edit.MENU
        case subjects.ROLES:
            to_first_menu_text = "To list of roles"
            to_first_menu_action = Menu.ROLES
            subject_text = "To role"
            subject_action = Role.Edit.MENU
        case subjects.INVENTORY:
            to_first_menu_text = "To inventory selection"
            to_first_menu_action = Menu.INVENTORY
        case subjects.RECEIPTS:
            to_first_menu_text = "To receipts department selection"
            to_first_menu_action = Menu.RECEIPTS
            subject_text = ["To list of receipts", "To receipt"]
            subject_action = [Receipt.Edit.DEPARTMENT, Receipt.Edit.MENU]
        case subjects.PRODUCTS:
            to_first_menu_text = "To list of products"
            to_first_menu_action = Menu.PRODUCTS
            subject_text = "To product"
            subject_action = Product.Edit.MENU
        case subjects.CATEGORIES:
            to_first_menu_text = "To list of categories"
            to_first_menu_action = Menu.CATEGORIES
            subject_text = "To category"
            subject_action = Category.Edit.MENU
        case subjects.DEPARTMENTS:
            to_first_menu_text = "To list of departments"
            to_first_menu_action = Menu.DEPARTMENTS
            subject_text = "To department"
            subject_action = Department.Edit.MENU

    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            "Back to menu", callback_data=cb.action.new(action=Menu.INIT)
        )
    )
    if subject:
        keyboard.add(
            InlineKeyboardButton(
                to_first_menu_text,
                callback_data=cb.menu_item.new(
                    state=Menu.CHOICE, action=to_first_menu_action, page=1
                ),
            )
        )
        if data:
            if type(data) == list:
                for each in range(len(data)):
                    keyboard.add(
                        InlineKeyboardButton(
                            subject_text[each],
                            callback_data=cb.generic.new(
                                state=subject_action[each],
                                action=subject_action[each],
                                data=data[each],
                            ),
                        )
                    )
            else:
                keyboard.add(
                    InlineKeyboardButton(
                        subject_text,
                        callback_data=cb.generic.new(
                            state=subject_action, action=subject_action, data=data
                        ),
                    )
                )
    return keyboard


kb_send_number = ReplyKeyboardMarkup(
    resize_keyboard=True, selective=True, one_time_keyboard=True
)
kb_send_number.add(KeyboardButton(text="Send phone number", request_contact=True))
kb_skip = ReplyKeyboardMarkup(
    resize_keyboard=True, selective=True, one_time_keyboard=True
)
kb_skip.add(KeyboardButton(text="Skip"))


def _get_pages(response, cb_type, cb_data):
    page_row = []

    if response["previous"] or response["next"]:
        if response["previous"]:
            prev_page = re.search(r"page=(\d+)", response["previous"])
            if prev_page:
                prev_page = prev_page.group(1)
            else:
                prev_page = 1
            cb_data["page"] = prev_page
            page_row.append(
                InlineKeyboardButton("<", callback_data=cb_type.new(**cb_data)),
            )
        if response["next"]:
            next_page = re.search(r"page=(\d+)", response["next"]).group(1)
            cb_data["page"] = next_page
            cur_page_data = {
                "state": CURRENT_PAGE,
                "action": "",
                "page": int(next_page) - 1,
            }
            page_row.append(
                InlineKeyboardButton(
                    str(int(next_page) - 1),
                    callback_data=cb.menu_item.new(**cur_page_data),
                ),
            )
            page_row.append(
                InlineKeyboardButton(">", callback_data=cb_type.new(**cb_data)),
            )
        else:
            cur_page_data = {
                "state": CURRENT_PAGE,
                "action": "",
                "page": int(prev_page) + 1,
            }
            page_row.append(
                InlineKeyboardButton(
                    str(int(prev_page) + 1),
                    callback_data=cb.menu_item.new(**cur_page_data),
                ),
            )
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
        DEPARTMENTS: Menu.DEPARTMENTS,
    }

    cb_data = {"state": Menu.CHOICE, "page": 1}

    permissions = tools.permissions(master)
    for subject in ALL_SUBJECTS.keys():
        if permissions[subject]:
            keyboard.add(
                InlineKeyboardButton(
                    ALL_SUBJECTS[subject],
                    callback_data=cb.menu_item.new(
                        action=get_menu_action[subject], **cb_data
                    ),
                )
            )

    return keyboard
