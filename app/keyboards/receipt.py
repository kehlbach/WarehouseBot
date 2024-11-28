from json import dumps

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.data import callbacks as cb
from app.data.constants import ADD, DELETE, EDIT, RECEIPTS, VIEW
from app.data.states import Generic, Menu, Receipt
from app.keyboards.menu import _get_pages, get_back
from app.utils import tools


def kb_back_to_receipts(master, receipt_id, department):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("To menu", callback_data=cb.action.new(action=Menu.INIT))
    )
    keyboard.add(
        InlineKeyboardButton(
            "Back to receipt choice",
            callback_data=cb.menu_item.new(
                state=Menu.CHOICE, action=Menu.RECEIPTS, page=1
            ),
        )
    )
    cb_edit_data = {
        "state": Receipt.Edit.MENU,
        "action": Receipt.Edit.MENU,
    }
    keyboard.add(
        InlineKeyboardButton(
            "To created receipt",
            callback_data=cb.generic.new(
                data=dumps([department, receipt_id]), **cb_edit_data
            ),
        )
    )
    permissions = tools.permissions(master)
    if ADD in permissions[RECEIPTS]:
        cb_add_data = {
            "state": Receipt.Create.INIT,
            "action": Receipt.Create.INIT,
            "data": "",
        }
        keyboard.add(
            InlineKeyboardButton(
                "Add receipt", callback_data=cb.generic.new(**cb_add_data)
            )
        )
    return keyboard


def get_receipt_department(
    master: dict, departments_page: dict, page: int
) -> InlineKeyboardMarkup:
    keyboard = get_back()
    permissions = tools.permissions(master)

    page_row = _get_pages(
        departments_page,
        cb.menu_item,
        dict(
            state=Menu.CHOICE,
            action=Menu.RECEIPTS,
            page=page,
        ),
    )

    if ADD in permissions[RECEIPTS]:
        cb_add_data = {
            "state": Receipt.Create.INIT,
            "action": Receipt.Create.INIT,
            "data": "",
        }
        keyboard.add(
            InlineKeyboardButton(
                "Add receipt", callback_data=cb.generic.new(**cb_add_data)
            )
        )

    if set([VIEW, EDIT, DELETE]).intersection(permissions[RECEIPTS]):
        cb_edit_data = {
            "state": Receipt.Edit.DEPARTMENT,
            "action": Receipt.Edit.DEPARTMENT,
        }
        keyboard.add(
            InlineKeyboardButton(
                "All available departments",
                callback_data=cb.generic.new(data="", **cb_edit_data),
            )
        )
        for each in departments_page["results"]:
            receipts_count = each["receipts_count"]
            if each["id"] in master["departments"] and not (each["is_hidden"]):
                keyboard.add(
                    InlineKeyboardButton(
                        "{}: receipts - {} ".format(each["repr"], receipts_count),
                        callback_data=cb.generic.new(data=each["id"], **cb_edit_data),
                    )
                )

    if page_row:
        keyboard.row(*page_row)

    return keyboard


def get_receipts(
    master: dict, receipts_page: dict, page: int, department
) -> InlineKeyboardMarkup:
    keyboard = get_back(RECEIPTS)
    permissions = tools.permissions(master)

    page_row = _get_pages(
        receipts_page,
        cb.menu_item,
        dict(
            state=Menu.CHOICE,
            action=Menu.RECEIPTS,
            page=page,
        ),
    )

    if set([VIEW, EDIT, DELETE]).intersection(permissions[RECEIPTS]):
        cb_edit_data = {
            "state": Receipt.Edit.MENU,
            "action": Receipt.Edit.MENU,
        }
        for each in receipts_page["results"]:
            keyboard.add(
                InlineKeyboardButton(
                    each["repr"],
                    callback_data=cb.generic.new(
                        data=dumps([department, each["id"]]), **cb_edit_data
                    ),
                )
            )

    if page_row:
        keyboard.row(*page_row)

    return keyboard


def kb_edit_receipt(master, receipt, department=""):
    if department:
        keyboard = get_back(RECEIPTS, data=[department])
    else:
        keyboard = get_back(RECEIPTS)
    permissions = tools.permissions(master)

    cb_data = {"receipt_id": receipt["id"]}
    receipt_id = cb_data["receipt_id"]
    receipt_id_jsoned = dumps([receipt_id])

    if EDIT in permissions[RECEIPTS]:
        note_cb = cb.generic.new(
            state=Generic.CALLBACK_TO_MESSAGE_INIT,
            action=Receipt.Edit.NOTE,
            data=receipt_id_jsoned,
        )

        keyboard.add(InlineKeyboardButton("Change note", callback_data=note_cb))

    if DELETE in permissions[RECEIPTS]:
        del_cb = cb.generic.new(
            state=Receipt.Edit.DELETE, action=Receipt.Edit.DELETE, data=receipt_id
        )
        keyboard.add(InlineKeyboardButton("Delete receipt", callback_data=del_cb))

    return keyboard


def kb_get_types():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            "Cancel",
            callback_data=cb.menu_item.new(
                state=Menu.CHOICE,
                action=Menu.RECEIPTS,
                page=1,
            ),
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            "Incoming",
            callback_data=cb.generic.new(
                state=Receipt.Create.TYPE,
                action=Receipt.Create.TO_DEP,
                data=1,
            ),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            "Transfer",
            callback_data=cb.generic.new(
                state=Receipt.Create.TYPE,
                action=Receipt.Create.FROM_DEP,
                data=1,
            ),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            "Outgoing",
            callback_data=cb.generic.new(
                state=Receipt.Create.TYPE,
                action=Receipt.Create.FROM_DEP_ONLY,
                data=1,
            ),
        )
    )

    return keyboard


def kb_get_create_department(
    master: dict, departments_page: dict, action: str, page: int, receipt_id
) -> InlineKeyboardMarkup:
    """Возвращает список отделений для выбора отделения для накладной"""
    if action in [
        Receipt.Create.TO_DEP,
        Receipt.Create.FROM_DEP,
        Receipt.Create.FROM_DEP_ONLY,
    ]:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton(
                "Cancel",
                callback_data=cb.generic.new(
                    state=Receipt.Edit.DELETE,
                    action=Receipt.Edit.DELETE,
                    data=receipt_id,
                ),
            )
        )
    else:
        keyboard = get_back()
    permissions = tools.permissions(master)

    page_row = _get_pages(
        departments_page,
        cb.menu_item,
        dict(
            state=Receipt.Create.TYPE,
            action=action,
            page=page,
        ),
    )

    if set([VIEW, EDIT, DELETE]).intersection(permissions[RECEIPTS]):
        cb_edit_data = {
            "state": Receipt.Create.DEPARTMENT,
            "action": action,
        }
        for each in departments_page["results"]:
            if each["id"] in master["departments"] and not (each["is_hidden"]):
                keyboard.add(
                    InlineKeyboardButton(
                        each["repr"],
                        callback_data=cb.receipt_department.new(
                            receipt_id=receipt_id,
                            department_id=each["id"],
                            page=page,
                            **cb_edit_data
                        ),
                    )
                )

    if page_row:
        keyboard.row(*page_row)

    return keyboard


def kb_add_product(
    master, products_page, receipt_id, page, remainings=[]
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    permissions = tools.permissions(master)

    page_row = _get_pages(
        products_page,
        cb.receipt_department,
        dict(
            state=Receipt.Create.DEPARTMENT,
            action=Receipt.Create.DEPARTMENT,
            receipt_id=receipt_id,
            department_id="",
            page=page,
        ),
    )
    keyboard.add(
        InlineKeyboardButton(
            "Cancel",
            callback_data=cb.generic.new(
                state=Receipt.Edit.DELETE, action=Receipt.Edit.DELETE, data=receipt_id
            ),
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            "Done",
            callback_data=cb.generic.new(
                state=Receipt.Create.PRODUCT,
                action=Receipt.Create.DONE,
                data=dumps([receipt_id]),
            ),
        )
    )

    if set([VIEW, EDIT, DELETE]).intersection(permissions[RECEIPTS]):
        cb_edit_data = {
            "state": Receipt.Create.PRODUCT,
            "action": Receipt.Create.PRODUCT,
        }

        if remainings:
            remainings = {each["product"]: each["quantity"] for each in remainings}
            for each in products_page["results"]:
                if each["id"] in remainings and remainings[each["id"]]:
                    keyboard.add(
                        InlineKeyboardButton(
                            "{}: available {}".format(
                                each["repr"], remainings[each["id"]]
                            ),
                            callback_data=cb.generic.new(
                                data=dumps(
                                    [receipt_id, each["id"], remainings[each["id"]]]
                                ),
                                **cb_edit_data
                            ),
                        )
                    )
        else:
            for each in products_page["results"]:
                keyboard.add(
                    InlineKeyboardButton(
                        each["repr"],
                        callback_data=cb.generic.new(
                            data=dumps([receipt_id, each["id"]]), **cb_edit_data
                        ),
                    )
                )

    if page_row:
        keyboard.row(*page_row)

    return keyboard
