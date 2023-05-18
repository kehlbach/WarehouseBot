""" cb_generic for generic message handler """

from aiogram.utils.callback_data import CallbackData

base = CallbackData('post', 'action', 'data', 'keyboard', sep='|')
""">>> ('action', 'data', 'keyboard')"""


action = CallbackData('post', 'action', sep='|')
""">>> ('action')"""

generic = CallbackData('post', 'state', 'action', 'data', sep='|')
""">>> ('state', 'action', 'data')"""

menu_item = CallbackData('post', 'state', 'action', 'page', sep='|')
""" >>> ('state', 'action', 'page')"""

user_role = CallbackData(
    'post',
    'state',
    'action',
    'page',
    'profile_id',
    'role_id')
""">>> ('state', 'action', 'page', 'profile_id', 'role_id')"""

product_category = CallbackData(
    'post',
    'state',
    'action',
    'page',
    'product_id',
    'category_id')
""">>> ('state', 'action', 'page', 'product_id', 'category_id')"""


user_departments = CallbackData(
    'post',
    'state',
    'action',
    'page',
    'profile_id',
    'department_id',
    'phone_number')
""">>> ('state', 'action', 'page', 'profile_id', 'department_id', 'phone_number')"""

role_permissions = CallbackData(
    'post',
    'state',
    'action',
    'role_id',
    'subject_id',
    'action_id'
)
""">>> ('state', 'action', 'role_id', 'subject_id', 'action_id')"""

receipt_department = CallbackData(
    'post',
    'state',
    'action',
    'receipt_id',
    'department_id',
    'page'
)
""" >>> ('state', 'action', 'receipt_id', 'department_id', 'page')"""