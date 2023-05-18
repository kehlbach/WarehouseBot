from aiogram.dispatcher.filters.state import State, StatesGroup

class Create(StatesGroup):
    INIT = 'RC0'
    TYPE = 'RC1'
    DEPARTMENT = 'RC2'
    FROM_DEP_ONLY = 'RC3'
    FROM_DEP = 'RC4'
    TO_DEP = 'RC5'
    PRODUCT = 'RC6'
    #QUANTITY = 'RC7'
    quantity = State()
    note = State()
    DONE = 'RC8'
    PRODUCT_ABORT = 'RC9'



class Edit(StatesGroup):
    DEPARTMENT = 'RD1'
    MENU = 'RD2'
    NOTE = 'RD3'
    DELETE = 'RD4'
