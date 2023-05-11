"""
Here are functions to validate or/and format different kinds of data passed to generic handlers
"""

import logging
import re

import phonenumbers
from app.utils import NAME_PATTERN
from app.loader import db
from aiogram import filters, md, types


def name_validator(name) -> tuple[str,bool,str]:
    """Returns name, is_valid, error_text"""
    if re.match(NAME_PATTERN, name):
        is_valid = True
        return name, is_valid, ''
    else:
        is_valid = False
        error_text = 'Не соответствует шаблону "Фамилия Имя Отчество"\n' +\
            'Введите ФИО. Пример:\n Иванов Иван Иванович'
        return name, is_valid, error_text


def number_preprocessor(message: types.Message, source_number: str = '',profiles = [], login = False) -> tuple[str,bool,str]:
    if message.contact:
        number = message.contact.phone_number
    else:
        number = message.text
    """Returns formatted_number, is_valid, error_text"""
    try:
        parsed_number = phonenumbers.parse(number, "KZ")
    except phonenumbers.NumberParseException:
        is_valid=False
        error_text = 'Некорректный номер. Попробуйте снова.'
    except Exception as e:
        is_valid=False
        error_text = e
        logging.warning('🔴Unknown exception in number_preprocessor')
    formatted_number = phonenumbers.format_number(
        parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    if source_number == formatted_number:
        is_valid=False
        error_text = 'Номер совпадает с прежним.'
    elif db.filter(db.PROFILES, phone_number=formatted_number) and not login:
        is_valid = False
        error_text = 'Такой номер уже зарегистрирован.'
    else:
        is_valid = True
        error_text = ''
    return formatted_number, is_valid, error_text
    
