from datetime import datetime
from json import loads
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
import logging
from app.data import callbacks as cb
from app.data.constants import DELETE, EDIT, VIEW, RECEIPTS
# from app.keyboards import *
from app import keyboards as kb
from app.data.states import Inventory
from app.loader import bot, db, dp
from app.utils import tools
from aiogram.types import InputFile

@dp.callback_query_handler(cb.generic.filter(state=Inventory.View.DEPARTMENT), state='*')
async def view_by_department(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = callback_query['from']['id']
    master = db.filter(db.PROFILES, user_id=user_id)
    if callback_data['data']:  # specific department
        department = db.get(db.DEPARTMENTS, callback_data['data'])
        text = 'Отделение: {}\nОстатки'.format(department['repr'])
        data = db.filter(db.INVENTORY_SUMMARY, department=department['id'])
        headers = ["Товар", "Количество", "Ед. изм."]
        rows = [[d["product_name"], d["quantity"], d['product_units']] for d in data]
    else:
        text = 'Все отделения\nОстатки'
        data = db.filter(db.INVENTORY_SUMMARY)
        headers = ['Отделение',"Товар", "Количество", "Ед. изм."]
        rows = [[d['department'],d["product_name"], d["quantity"], d['product_units']] for d in data]
    if data:
        image_buffer = tools.generate_png(headers, rows)
        reply_markup = kb.kb_view_inventory(master, department=callback_data['data'])
        await bot.delete_message(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id)
        await bot.send_photo(
            chat_id=callback_query.message.chat.id,
            caption=text,
            photo=InputFile(image_buffer, filename="summary.png"),
            reply_markup=reply_markup)
    else:
        text = 'Нет остатков'
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            text=text,
            reply_markup=kb.kb_view_inventory(master, department=callback_data['data']))
