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
from tabulate import tabulate
from PIL import Image, ImageDraw, ImageFont
import io
from aiogram.types import InputFile
import platform

@dp.callback_query_handler(cb.generic.filter(state=Inventory.View.DEPARTMENT), state='*')
async def view_by_department(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = callback_query['from']['id']
    master = db.filter(db.PROFILES, user_id=user_id)
    if callback_data['data']:  # specific department
        department = db.get(db.DEPARTMENTS, callback_data['data'])
        text = 'Отделение: {}\nОстатки'.format(department['repr'])
        data = db.filter(db.INVENTORY_SUMMARY, department=department['id'])
        headers = ["Товар", "Количество", "Ед. изм."]
        rows = [[d["product_name"], d["quantity"], "шт."] for d in data]
    else:
        text = 'Все отделения\nОстатки'
        data = db.filter(db.INVENTORY_SUMMARY)
        headers = ['Отделение',"Товар", "Количество", "Ед. изм."]
        rows = [[d['department'],d["product_name"], d["quantity"], "шт."] for d in data]
    if data:
        table = tabulate(rows, headers=headers)
        font_size = 20
        if platform.system() == "Windows":
            font = ImageFont.truetype("arial.ttf", font_size)
        elif platform.system() == "Linux":
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        cell_padding = 5  # Add some padding around the text in each cell
        line_height = font.getsize("hg")[1] + cell_padding * 2  # Height of each row
        header_height = font.getsize(max(headers, key=len))[1] + cell_padding * 2  # Height of header row
        cell_widths = [max(font.getsize(str(row[i]))[0] for row in rows + [headers]) + cell_padding * 2 for i in range(len(headers))]  # Width of each column
        image_width = sum(cell_widths)  # Width of table
        image_height = header_height + line_height * len(rows) + cell_padding * 2  # Height of table
        image = Image.new("RGB", (image_width, image_height), color="white")
        draw = ImageDraw.Draw(image)
        x = 0
        y = 0
        for i, header in enumerate(headers):
            cell_width = cell_widths[i]
            draw.rectangle((x, y, x + cell_width, y + header_height), fill=(0, 0, 0))
            draw.text((x + cell_padding, y + cell_padding), header, font=font, fill=(255, 255, 255))
            x += cell_width
        x = 0
        y += header_height
        for row in rows:
            for i, cell in enumerate(row):
                cell_width = cell_widths[i]
                draw.rectangle((x, y, x + cell_width, y + line_height), fill=(255, 255, 255), outline=(0, 0, 0))
                draw.text((x + cell_padding, y + cell_padding), str(cell), font=font, fill=(0, 0, 0))
                x += cell_width
            x = 0
            y += line_height
        image_buffer = io.BytesIO()
        image.save(image_buffer, format="PNG")
        image_buffer.seek(0)

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
