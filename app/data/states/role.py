from aiogram.dispatcher.filters.state import State, StatesGroup

class Create(StatesGroup):
    NAME= 'RC1'

    name = State()
    class Permissions:
        MENU = 'RCP1'
        SUBJECT = 'RCP5'
        DONE = 'RCP2'
        ALL = 'RCP3'
        SPECIFIC = 'RCP4'
        BACK = 'RCP6'

class Edit(StatesGroup):
    MENU = 'RE1'
    NAME = 'RE2'
    SPECIFIC = 'RE4'
    DELETE = 'RE5'
    class Permissions:
        MENU = 'REP1'
        SUBJECT = 'REP5'
        DONE = 'REP2'
        ALL = 'REP3'
        SPECIFIC = 'REP4'
        BACK = 'REP6'