from aiogram.dispatcher.filters.state import State, StatesGroup


class Login(StatesGroup):
    number = State()
    name = State()
    check = State()
    NUMBER = 'L1'
    NAME = 'L2'
    CHECK = 'L3'
