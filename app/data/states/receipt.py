from aiogram.dispatcher.filters.state import State, StatesGroup

class Create(StatesGroup):
    INIT = 'REC0'
    TYPE = 'REC1'
    DEPARTMENT = 'REC2'
    FROM_DEP_ONLY = 'REC3'
    FROM_DEP = 'REC4'
    TO_DEP = 'REC5'
    PRODUCT = 'REC6'
    quantity = State()
    note = State()
    DONE = 'REC8'
    PRODUCT_ABORT = 'REC9'



class Edit(StatesGroup):
    DEPARTMENT = 'RED1'
    MENU = 'RED2'
    NOTE = 'RED3'
    DELETE = 'RED4'
