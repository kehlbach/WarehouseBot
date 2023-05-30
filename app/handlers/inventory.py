from datetime import datetime
from json import loads
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
import logging, re
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
        rows = [[d['department_name'],d["product_name"], d["quantity"], d['product_units']] for d in data]
    if data:
        image_buffer = tools.generate_png(headers, rows)
        reply_markup = kb.kb_view_inventory(master, department=callback_data['data'])
        try:
            await bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id)
        finally:
            await bot.send_photo(
                chat_id=callback_query.message.chat.id,
                caption=text,
                photo=InputFile(image_buffer, filename="summary.png"),
                reply_markup=reply_markup)
    else:
        text = 'Нет остатков'
        keyboard = kb.kb_view_inventory(master, department=callback_data['data'])
        try:
            await bot.edit_message_text(
                chat_id=callback_query.message.chat.id,
                text=text,
                reply_markup=keyboard)
        except:
            try:
                bot.delete_message(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.message_id)
            finally:
                bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text=text,
                    reply_markup=keyboard)

@dp.callback_query_handler(cb.generic.filter(state=Inventory.View.BY_DATE), state='*')
async def ask_date(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = callback_query['from']['id']
    master = db.filter(db.PROFILES, user_id=user_id)
    await Inventory.View.Date.set()
    await state.set_data({'department': callback_data['data']})
    return await callback_query.message.answer('Введите дату в формате YYYY-MM-DD')

@dp.message_handler(state=Inventory.View.Date)
async def view_by_date(message: Message, state: FSMContext):
    if not re.match(r'\d{4}-\d{2}-\d{2}', message.text):
        return await message.answer('Неверный формат даты')
    user_id = message['from']['id']
    master = db.filter(db.PROFILES, user_id=user_id)
    data = await state.get_data()
    department_id = data['department']
    if department_id:  # specific department
        department = db.get(db.DEPARTMENTS, department_id)
        text = 'Отделение: {}\nОстатки\nДата - {}'.format(department['repr'], message.text)
        data = db.filter(db.INVENTORY_SUMMARY, department=department['id'], date=message.text)
        headers = ["Товар", "Количество", "Ед. изм."]
        rows = [[d["product_name"], d["quantity"], d['product_units']] for d in data]
    else:
        text = 'Все отделения\nОстатки'
        data = db.filter(db.INVENTORY_SUMMARY, date=message.text)
        headers = ['Отделение',"Товар", "Количество", "Ед. изм."]
        rows = [[d['department_name'],d["product_name"], d["quantity"], d['product_units']] for d in data]
    if data:
        image_buffer = tools.generate_png(headers, rows)
        reply_markup = kb.kb_view_inventory(master, department=department_id)
        return await bot.send_photo(
            chat_id=message.chat.id,
            caption=text,
            photo=InputFile(image_buffer, filename="summary.png"),
            reply_markup=reply_markup)
    else:
        text = 'Нет остатков до {}'.format(message.text)

        return await bot.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=reply_markup)


@dp.callback_query_handler(cb.generic.filter(state=Inventory.View.EXPORT), state='*')
async def export_inventory(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    return await callback_query.answer('Not implemented')