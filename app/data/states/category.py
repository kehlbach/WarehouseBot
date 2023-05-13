""">>> MENU, new, name"""

from aiogram.dispatcher.filters.state import State, StatesGroup


class Create(StatesGroup):
    name = State()
    NAME = 'C1'


class Edit(StatesGroup):
    MENU = 'C2'
    NAME = 'C3'
    DELETE = 'C4'
