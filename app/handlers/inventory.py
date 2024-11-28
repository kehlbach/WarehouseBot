import re

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InputFile, Message

from app.data import callbacks as cb
from app.data.states import Inventory
from app.keyboards.inventory import kb_view_inventory
from app.loader import bot, db, dp
from app.utils import tools


@dp.callback_query_handler(
    cb.generic.filter(state=Inventory.View.DEPARTMENT), state="*"
)
async def view_by_department(
    callback_query: CallbackQuery, callback_data: dict, state: FSMContext
):
    user_id = callback_query["from"]["id"]
    master = db.filter(db.PROFILES, user_id=user_id)
    if callback_data["data"]:  # specific department
        department = db.get(db.DEPARTMENTS, callback_data["data"])
        text = "Department: {}\nInventory".format(department["repr"])
        data = db.filter(db.INVENTORY_SUMMARY, department=department["id"])
        headers = ["Product", "Quantity", "Unit"]
        rows = [[d["product_name"], d["quantity"], d["product_units"]] for d in data]
    else:
        text = "All departments\nInventory"
        data = db.filter(db.INVENTORY_SUMMARY)
        headers = ["Department", "Product", "Quantity", "Unit"]
        rows = [
            [d["department_name"], d["product_name"], d["quantity"], d["product_units"]]
            for d in data
        ]
    if data:
        image_buffer = tools.generate_png(headers, rows)
        reply_markup = kb_view_inventory(master, department=callback_data["data"])
        try:
            await bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
            )
        finally:
            await bot.send_photo(
                chat_id=callback_query.message.chat.id,
                caption=text,
                photo=InputFile(image_buffer, filename="summary.png"),
                reply_markup=reply_markup,
            )
    else:
        text = "Inventory is empty"
        keyboard = kb_view_inventory(master, department=callback_data["data"])
        try:
            await bot.edit_message_text(
                chat_id=callback_query.message.chat.id, text=text, reply_markup=keyboard
            )
        except:
            try:
                bot.delete_message(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.message_id,
                )
            finally:
                bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text=text,
                    reply_markup=keyboard,
                )


@dp.callback_query_handler(cb.generic.filter(state=Inventory.View.BY_DATE), state="*")
async def ask_date(
    callback_query: CallbackQuery, callback_data: dict, state: FSMContext
):
    user_id = callback_query["from"]["id"]
    master = db.filter(db.PROFILES, user_id=user_id)
    await Inventory.View.Date.set()
    await state.set_data({"department": callback_data["data"]})
    return await callback_query.message.answer("Enter date in YYYY-MM-DD format")


@dp.message_handler(state=Inventory.View.Date)
async def view_by_date(message: Message, state: FSMContext):
    if not re.match(r"\d{4}-\d{2}-\d{2}", message.text):
        return await message.answer("Invalid date format")
    user_id = message["from"]["id"]
    master = db.filter(db.PROFILES, user_id=user_id)
    data = await state.get_data()
    department_id = data["department"]
    if department_id:  # specific department
        department = db.get(db.DEPARTMENTS, department_id)
        text = "Department: {}\nInventory\nDate - {}".format(
            department["repr"], message.text
        )
        data = db.filter(
            db.INVENTORY_SUMMARY, department=department["id"], date=message.text
        )
        headers = ["Product", "Quantity", "Unit"]
        rows = [[d["product_name"], d["quantity"], d["product_units"]] for d in data]
    else:
        text = "All departments\nInventory"
        data = db.filter(db.INVENTORY_SUMMARY, date=message.text)
        headers = ["Department", "Product", "Quantity", "Unit"]
        rows = [
            [d["department_name"], d["product_name"], d["quantity"], d["product_units"]]
            for d in data
        ]
    reply_markup = kb_view_inventory(master, department=department_id)
    if data:
        image_buffer = tools.generate_png(headers, rows)
        return await bot.send_photo(
            chat_id=message.chat.id,
            caption=text,
            photo=InputFile(image_buffer, filename="summary.png"),
            reply_markup=reply_markup,
        )
    else:
        text = "No inventory as of {}".format(message.text)

        return await bot.send_message(
            chat_id=message.chat.id, text=text, reply_markup=reply_markup
        )


@dp.callback_query_handler(cb.generic.filter(state=Inventory.View.EXPORT), state="*")
async def export_inventory(
    callback_query: CallbackQuery, callback_data: dict, state: FSMContext
):
    return await callback_query.answer("Not implemented")
