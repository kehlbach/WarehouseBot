""">>> CALLBACK_TO_MESSAGE_INIT, CALLBACK_HANDLE, MESSAGE_HANDLE 
>>> message_handle"""

from aiogram.dispatcher.filters.state import State, StatesGroup

class Generic(StatesGroup):
    CALLBACK_TO_MESSAGE_INIT = 'G1'
    """generic handler catches and sends message"""
    CALLBACK_HANDLE = 'G2'
    message_handle = State()
    """generic handler processes message answer from user"""
