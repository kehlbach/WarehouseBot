from aiogram.dispatcher.filters.state import State, StatesGroup


class Create(StatesGroup):
    NAME = "ROC1"

    name = State()

    class Permissions:
        MENU = "ROCP1"
        SUBJECT = "ROCP5"
        DONE = "ROCP2"
        ALL = "ROCP3"
        SPECIFIC = "ROCP4"
        BACK = "ROCP6"


class Edit(StatesGroup):
    MENU = "ROE1"
    NAME = "ROE2"
    SPECIFIC = "ROE4"
    DELETE = "ROE5"

    class Permissions:
        MENU = "ROEP1"
        SUBJECT = "ROEP5"
        DONE = "ROEP2"
        ALL = "ROEP3"
        SPECIFIC = "ROEP4"
        BACK = "ROEP6"
