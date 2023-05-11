
# from requests import Response
# from app.bot import session
import json
import re
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import types
from functools import wraps
from app.data.states import Login
from app.utils import NAME_PATTERN
from app.loader import db

def shorten_name(name):
    group = re.split(NAME_PATTERN,name)
    return '{} {}. {}.'.format(group[1],group[2][0],group[3][0])

# was when role permissions was nested object
# def permissions (role):
#     #returns dict like:
#     #{'добавлять': ['Департаменты', 'Категории'.. ], 'изменять': [..]
#     result = dict()
#     for each in role['permissions']:
#         result[each['subject']] = result.get(each['subject'],[])+[each['action']]
#         #each['subject']
#     return result


# input is now like 'subject1:read,write subject2:read,delete '. Rewrite it according to changes
profile = {}
profile['permissions'] = "{\"20\": [10, 11, 12, 13], \"21\": [10, 11, 12, 13], \"22\": [10, 11, 12, 13], \"23\": [10, 11, 12, 13], \"24\": [10, 11, 12, 13], \"25\": [10, 11, 12, 13], \"26\": [10, 11, 12, 13]}"
def permissions (profile):
    return dict(json.loads(profile['permissions']))



# was when role permissions was nested object
# def has_permission(role: dict, action: str, subject: str) -> bool:
#     if action != '*':
#         if any(d['action'] == action and d['subject'] == subject for d in role['permissions']):
#             return True
#     else:
#         for each in role['permissions']:
#             if each['subject'] == subject:
#                 return True    
#     return False



def has_permissions():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if isinstance(args[0],types.Message):
                state = kwargs['state']
                current_state = await state.get_state()
                if current_state not in (Login.number.state,Login.name.state):
                    message = args[0]
                    user_id = message.from_id
                    profile = db.filter(db.PROFILES, user_id=user_id)
                    if not(profile and profile['permissions']):
                        return await message.answer('Нет прав.')                    
            elif isinstance(args[0],types.CallbackQuery):
                callback_query = args[0]
                user_id = callback_query.from_user.id
                profile = db.filter(db.PROFILES, user_id=user_id)
                if not(profile and profile['permissions']):
                    return await callback_query.answer('Нет прав.')
            return await func(*args, **kwargs)
        return wrapper
    return decorator
# def has_permissions2(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         master = kwargs['master']
#         if master['role']['permissions']:
#             return func(*args, **kwargs)
#         else:
#             keyboard = InlineKeyboardMarkup()
#             text = 'Добро пожаловать. У вас пока нет прав.'
#             keyboard.add(InlineKeyboardButton(
#             text='Проверить статус', callback_data='check_status'))
#             return {'text': text, 'reply_markup': keyboard}
#     return wrapper

# def db_get(table, id=''):
#     # without id:
#     # {'count': 3, 'next': None, 'previous': None, 'results': [{...}, {...}, {...}]}
#     url = f'{DB_API_URL}/{table}'
#     if id:
#         # with_id:
#         # {'id': 1, 'name': 'administrator', 'perms': []}
#         url += f'/{id}'
#         response = session.get(url)
#         return response.json()
#     else:
#         result = []
#         next = True
#         while next:
#             response = session.get(url).json()
#             result = result + response['results']
#             next = bool(response['next'])
#             url = response['next']
#         return result

# def db_get_page(table, page='1'):
#     url = f'{DB_API_URL}/{table}/?page={page}'
#     return session.get(url).json()
# def db_next_page(response):
#     if type(response == Response):
#         logging.error('🟥Not JSON-ized db thing!')
#         response = response.json()
#     next = response['next']
#     return session.get(next).json()
# def db_prev_page(response):
#     if type(response == Response):
#         logging.error('🟥Not JSON-ized db thing!')
#         response = response.json()
#     previous = response['previous']
#     return session.get(previous).json()


# def db_filter(table, column, text):
#     text = text.replace('+', r'%2B')
#     response = session.get(f'{DB_API_URL}/{table}/?{column}={text}')
#     result = response.json()['results']
#     if len(result) == 1:
#         return response.json()['results'][0]
#     else:
#         return response.json()['results']


# def db_add(table, data):
#     return session.post(f'{DB_API_URL}/{table}/', data=data)


# def db_edit(table, id, data):
#     return session.put(f'{DB_API_URL}/{table}/{id}/', data=data)


# def db_delete(table, id):
#     return session.delete(f'{DB_API_URL}/{table}/{id}/')
