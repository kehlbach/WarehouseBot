from aiogram.dispatcher.filters.state import State, StatesGroup


class Create(StatesGroup):
    name = State()
    NAME = "DC1"
    LOCATION = "DC2"


class Edit(StatesGroup):
    MENU = "DE2"
    NAME = "DE3"
    LOCATION = "DE4"
    DELETE = "DE5"
