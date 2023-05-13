import json
import re
from functools import wraps

from aiogram import types

from app.data.states import Login



def shorten_name(name):
    from app.utils import NAME_PATTERN
    group = re.split(NAME_PATTERN, name)
    return '{} {}. {}.'.format(group[1], group[2][0], group[3][0])


profile = {}
profile['permissions'] = "{\"20\": [10, 11, 12, 13], \"21\": [10, 11, 12, 13], \"22\": [10, 11, 12, 13], \"23\": [10, 11, 12, 13], \"24\": [10, 11, 12, 13], \"25\": [10, 11, 12, 13], \"26\": [10, 11, 12, 13]}"


def permissions(profile):
    return dict(json.loads(profile['permissions']))


def has_permissions():
    from app.loader import db
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if isinstance(args[0], types.Message):
                state = kwargs['state']
                current_state = await state.get_state()
                if current_state not in (Login.number.state, Login.name.state):
                    message = args[0]
                    user_id = message.from_id
                    profile = db.filter(db.PROFILES, user_id=user_id)
                    if not (profile and profile['permissions']):
                        return await message.answer('Нет прав.')
            elif isinstance(args[0], types.CallbackQuery):
                callback_query = args[0]
                user_id = callback_query.from_user.id
                profile = db.filter(db.PROFILES, user_id=user_id)
                if not (profile and profile['permissions']):
                    return await callback_query.answer('Нет прав.')
            return await func(*args, **kwargs)
        return wrapper
    return decorator
