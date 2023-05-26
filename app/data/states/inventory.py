from aiogram.dispatcher.filters.state import State, StatesGroup

class View(StatesGroup):
    DEPARTMENT = 'ID1'
    BY_DATE = 'ID2'
    Date = State()
    EXPORT = 'ID3'