"""
for callback_query_handler (including generic message init handler):
>>> STATE = 'S1'

for message_handler
>>> state = State()
"""

from aiogram.dispatcher.filters.state import State, StatesGroup

from . import user as User
from . import category as Category
from . import role as Role
from . import department as Department
from . import product as Product
from . import receipt as Receipt
from . import inventory as Inventory
from .generic import *
from .login import *
from .menu import *
