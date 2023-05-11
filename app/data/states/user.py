"""Create, Edit"""

from aiogram.dispatcher.filters.state import State, StatesGroup
#START = 'UC1'


class Create:
    """ >>> NUMBER, NAME
    >>> Departments: MENU, DONE, ALL, SPECIFIC
    >>> Roles: MENU, SPECIFIC """

    NUMBER = 'UC2'
    NAME = 'UC5'
    
    class Departments:
        MENU = 'UCD'
        DONE = 'UCD1'
        ALL = 'UCD2'
        SPECIFIC = 'UCD3'


    class Roles:
        MENU = 'UCR'
        SPECIFIC = 'UCR1'
class Edit:
    """ >>> MENU, NUMBER, NUMBER_OWN, NAME, DELETE
    >>> Departments: MENU, DONE, ALL, SPECIFIC
    >>> Roles: MENU, SPECIFIC """
    MENU = 'UE1'
    NUMBER = 'UE2'
    NUMBER_OWN = 'UE7'
    NAME = 'UE5'
    DELETE = 'UE6'


    class Departments:
        MENU = 'UED'
        DONE = 'UED1'
        ALL = 'UED2'
        SPECIFIC = 'UED3'
        
    class Roles:
        MENU = 'UER'
        SPECIFIC = 'UER1'
