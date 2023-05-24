import json
import re
from functools import wraps

from aiogram import types

from app.data.states import Login

from PIL import Image, ImageDraw, ImageFont
import io
import platform


def shorten_name(name):
    from app.utils import NAME_PATTERN
    group = re.split(NAME_PATTERN, name)
    return '{} {}. {}.'.format(group[1], group[2][0], group[3][0])


profile = {}
profile['permissions'] = "{\"20\": [10, 11, 12, 13], \"21\": [10, 11, 12, 13], \"22\": [10, 11, 12, 13], \"23\": [10, 11, 12, 13], \"24\": [10, 11, 12, 13], \"25\": [10, 11, 12, 13], \"26\": [10, 11, 12, 13]}"


def permissions(profile):
    return dict(json.loads(profile['permissions']))



def generate_png(headers, rows):
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
    return image_buffer