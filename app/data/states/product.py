from aiogram.dispatcher.filters.state import State, StatesGroup


class Create(StatesGroup):
    VENDOR_CODE = 'PC1'
    NAME = 'PC2'
    UNIT = 'PC3'

    class Category:
        MENU = 'PCD'
        SPECIFIC = 'PCD1'


class Edit(StatesGroup):
    MENU = 'PE1'
    VENDOR_CODE = 'PE2'
    NAME = 'PE3'
    UNIT = 'PE4'
    DELETE = 'PE5'

    class Category:
        MENU = 'PED'
        SPECIFIC = 'PED1'
