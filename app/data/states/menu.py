""">>> PROFILES, ROLES, INVENTORY, RECEIPTS, PRODUCTS, CATEGORIES, DEPARTMENTS, CHOICE"""

from aiogram.dispatcher.filters.state import State, StatesGroup

CURRENT_PAGE = "CP1"


class Menu:
    INIT = "M1"
    PROFILES = "M2"
    ROLES = "M3"
    INVENTORY = "M4"
    RECEIPTS = "M5"
    PRODUCTS = "M6"
    CATEGORIES = "M7"
    DEPARTMENTS = "M8"
    CHOICE = "M9"
