import logging
from json import loads

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message

from app.data import callbacks as cb
from app.data.constants import DELETE, EDIT, RECEIPTS, VIEW
from app.data.states import Receipt
from app.keyboards.menu import get_back, kb_skip
from app.keyboards.receipt import (get_receipts, kb_add_product,
                                   kb_back_to_receipts, kb_edit_receipt,
                                   kb_get_create_department, kb_get_types)
from app.loader import bot, db, dp
from app.utils import tools


@dp.callback_query_handler(cb.generic.filter(state=Receipt.Edit.DEPARTMENT), state='*')
async def work_on_receipts(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = callback_query['from']['id']
    master = db.filter(db.PROFILES, user_id=user_id)
    if callback_data['data']:  # Specific department
        receipts_page = db.get_page(db.RECEIPTS, callback_data.get('page', 1),
                                    department=callback_data['data'],
                                    allowed_to=master['id'])
        dep = db.get(db.DEPARTMENTS, callback_data['data'])
        text = 'Department: {}\nSelect receipt'.format(dep['repr'])
        reply_markup = get_receipts(master, receipts_page, callback_data.get('page', 1),
                                    department=callback_data['data'])
    else:  # All available departments
        receipts_page = db.get_page(db.RECEIPTS,
                                    callback_data.get('page', 1),
                                    allowed_to=master['id'])
        text = 'Receipts for all departments\nSelect receipt'
        reply_markup = get_receipts(master, receipts_page, callback_data.get('page', 1),
                                    department=callback_data['data'])
    return await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup)


@dp.callback_query_handler(cb.generic.filter(state=Receipt.Edit.MENU), state='*')
async def edit_receipt(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = callback_query['from']['id']
    master = db.filter(db.PROFILES, user_id=user_id)
    permissions = tools.permissions(master)
    callback_data['data'] = loads(callback_data['data'])
    if type(callback_data['data']) == list and len(callback_data['data']) == 2:
        department_id = callback_data['data'][0]
        receipt_id = callback_data['data'][1]
    elif type(callback_data['data']) == int:
        department_id = ''
        receipt_id = callback_data['data']
    if set([VIEW, EDIT, DELETE]).intersection(permissions[RECEIPTS]):
        receipt = db.get(db.RECEIPTS, receipt_id)
        text = 'Receipt'
        text += '\nType: ' + receipt['type']
        if receipt['from_department_name']:
            text += '\nFrom department: ' + receipt['from_department_name']
        if receipt['to_department_name']:
            text += '\nTo department: ' + receipt['to_department_name']
        if receipt['note']:
            text += '\nNote: ' + receipt['note']
        products = db.filter(db.RECEIPT_PRODUCTS, receipt=receipt['id'])
        # list all products in text like product: quantity
        products = [products] if type(products) != list else products
        text += '\nProducts:'
        for each in products:
            text += f'\n    {each["product_name"]}: {each["quantity"]} {each["product_units"]}'
        reply_markup = kb_edit_receipt(
            master, receipt=receipt, department=department_id)
    else:
        text = 'No access'
        reply_markup = None
    return await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@dp.callback_query_handler(cb.generic.filter(state=Receipt.Create.INIT), state='*')
async def create_receipt_type(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    action = callback_data['action']
    user_id = callback_query['from']['id']
    master = db.filter(db.PROFILES, user_id=user_id)
    if not master['departments']:
        return await callback_query.answer('Can\'t create receipt if no departments available')
    page = callback_data.get('page', 1)
    text = 'Choose receipt type'
    reply_markup = kb_get_types()
    return await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@dp.callback_query_handler(cb.generic.filter(state=Receipt.Create.TYPE), state='*')
async def create_receipt_type(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    action = callback_data['action']
    page = callback_data.get('data', 1)
    user_id = callback_query['from']['id']
    master = db.filter(db.PROFILES, user_id=user_id)
    receipt = db.add(db.RECEIPTS,
                     made_by=master['id'],
                     requester=callback_query.message.chat.id)
    departments_page = db.get_page(
        db.DEPARTMENTS, page, allowed_to=master['id'])
    reply_markup = kb_get_create_department(
        master, departments_page, action, page, receipt_id=receipt['id'])
    match action:
        case Receipt.Create.FROM_DEP:
            text = 'Select department from which products are received'
        case Receipt.Create.FROM_DEP_ONLY:
            text = 'Select department from which products are issued'
        case Receipt.Create.TO_DEP:
            text = 'Select department to which products are delivered'
    return await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@dp.callback_query_handler(cb.receipt_department.filter(state=Receipt.Create.DEPARTMENT), state='*')
async def create_department(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = callback_query['from']['id']
    master = db.filter(db.PROFILES, user_id=user_id)
    action = callback_data['action']
    receipt_id = callback_data['receipt_id']
    if action != Receipt.Create.DEPARTMENT:
        department_id = callback_data['department_id']
        if action in (Receipt.Create.FROM_DEP, Receipt.Create.FROM_DEP_ONLY):
            departments_summary = db.filter(
                db.INVENTORY_SUMMARY, department=department_id, return_list=True)
            non_empty_departments = set(
                [d['department'] for d in departments_summary if d['quantity'] > 0])
            if int(department_id) not in non_empty_departments:
                return await callback_query.answer('There are no products in this department')
    match action:
        case Receipt.Create.DEPARTMENT:
            text = 'Select product to add to receipt'
            products_page = db.get_page(db.PRODUCTS)
            receipt = db.get(db.RECEIPTS, receipt_id)
            if receipt['from_department']:
                dep_id = receipt['from_department']
                remainings = db.filter(
                    db.INVENTORY_SUMMARY, department=dep_id, return_list=True)
                reply_markup = kb_add_product(
                    master, products_page, receipt_id, 1, remainings)
            else:
                reply_markup = kb_add_product(
                    master, products_page, receipt_id, 1)
        case Receipt.Create.FROM_DEP:
            text = 'Receipt of goods\nSelect department from which products are received on the receipt'
            changed_receipt = db.edit_patch(db.RECEIPTS,
                                            receipt_id,
                                            from_department=department_id,
                                            requester=callback_query.message.chat.id)
            departments_page = db.get_page(
                db.DEPARTMENTS, 1, allowed_to=master['id'])
            reply_markup = kb_get_create_department(
                master, departments_page, Receipt.Create.TO_DEP, 1, receipt_id=receipt_id)
        case Receipt.Create.FROM_DEP_ONLY:
            text = 'Select product to add to receipt'
            changed_receipt = db.edit_patch(db.RECEIPTS, receipt_id,
                                            from_department=department_id,
                                            requester=callback_query.message.chat.id)
            products_page = db.get_page(db.PRODUCTS)
            if changed_receipt['from_department']:
                dep_id = changed_receipt['from_department']
                remainings = db.filter(
                    db.INVENTORY_SUMMARY, department=dep_id, return_list=True)
                reply_markup = kb_add_product(
                    master, products_page, receipt_id, 1, remainings)
            else:
                reply_markup = kb_add_product(
                    master, products_page, receipt_id, 1)
        case Receipt.Create.TO_DEP:
            text = 'Select product to add to receipt'
            receipt = db.get(db.RECEIPTS, receipt_id)
            if int(department_id) == receipt['from_department']:
                return await callback_query.answer('Source and destination departments can\'t be the same')
            changed_receipt = db.edit_patch(db.RECEIPTS, receipt_id,
                                            to_department=department_id,
                                            requester=callback_query.message.chat.id)
            products_page = db.get_page(db.PRODUCTS)
            if changed_receipt['from_department']:
                dep_id = changed_receipt['from_department']
                remainings = db.filter(
                    db.INVENTORY_SUMMARY, department=dep_id, return_list=True)
                reply_markup = kb_add_product(
                    master, products_page, receipt_id, 1, remainings)
            else:
                reply_markup = kb_add_product(
                    master, products_page, receipt_id, 1)

    return await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )


@dp.callback_query_handler(cb.generic.filter(state=Receipt.Create.PRODUCT), state='*')
async def handler_create_product(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = callback_query['from']['id']
    master = db.filter(db.PROFILES, user_id=user_id)
    callback_data['data'] = loads(callback_data['data'])
    receipt_id = callback_data['data'][0]
    action = callback_data['action']
    match action:
        case Receipt.Create.DONE:
            if not db.filter(db.RECEIPT_PRODUCTS, receipt=receipt_id):
                return await callback_query.answer('Add products first')
            else:
                text = 'Enter receipt\'s note'
                reply_markup = kb_skip
                await Receipt.Create.note.set()
                async with state.proxy() as data:
                    data['receipt_id'] = receipt_id
                    data['master_id'] = master['id']
            await bot.delete_message(
                chat_id=callback_query.from_user.id,
                message_id=callback_query.message.message_id)
            return await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=text,
                reply_markup=reply_markup
            )
        case Receipt.Create.PRODUCT:
            product_id = callback_data['data'][1]
            text = 'Enter quantity of product\nIf selected product was a mistake, enter 0'
            await Receipt.Create.quantity.set()
            async with state.proxy() as data:
                data['receipt_id'] = receipt_id
                data['master_id'] = master['id']
                data['product_id'] = product_id
                if len(callback_data['data']) > 2:
                    available = callback_data['data'][2]
                    rp = db.filter(db.RECEIPT_PRODUCTS,
                                   receipt=receipt_id, product=product_id)
                    quantity = rp['quantity'] if rp else 0
                    data['available'] = int(available)
                    text = text.replace(
                        '\n', '\nAvailable: {}\n'.format(available+quantity))
            reply_markup = None
            return await bot.edit_message_text(
                chat_id=callback_query.from_user.id,
                message_id=callback_query.message.message_id,
                text=text,
                reply_markup=reply_markup
            )


@dp.message_handler(state=Receipt.Create.quantity)
async def create_product_quantity(message: Message, state: FSMContext):
    data = await state.get_data()
    receipt_id = data['receipt_id']
    product_id = data['product_id']
    master_id = data['master_id']
    available = data['available'] if 'available' in data else -1
    master = db.get(db.PROFILES, id=master_id)
    quantity = message.text
    if quantity.isdigit():
        quantity = int(quantity)
        if quantity != 0:
            rp = db.filter(db.RECEIPT_PRODUCTS,
                           receipt=receipt_id, product=product_id)
            quantity_old = rp['quantity'] if rp else 0
            if 'available' in data and data['available']+quantity_old >= quantity or not ('available' in data):
                receipt_product = db.add(db.RECEIPT_PRODUCTS,
                                         receipt=receipt_id,
                                         product=product_id,
                                         quantity=quantity,
                                         requester=message.chat.id)
                if 'non_field_errors' in receipt_product:
                    if receipt_product['non_field_errors'][0] == 'The fields receipt, product, price must make a unique set.':
                        db.delete(db.RECEIPT_PRODUCTS,
                                  id=rp['id'], requester=message.chat.id)
                        receipt_product = db.add(db.RECEIPT_PRODUCTS,
                                                 receipt=receipt_id,
                                                 product=product_id,
                                                 quantity=quantity+quantity_old,
                                                 requester=message.chat.id)
                        text = 'Product data for "{}" was corrected'.format(
                            receipt_product['product_name'])
                else:
                    text = 'Product "{}" added to receipt'.format(
                        receipt_product['product_name'])
            else:
                text = 'Not enough products in stock'
        else:
            text = 'Adding product cancelled'
        text += '\nSelect product to add to receipt'
        rps = db.filter(db.RECEIPT_PRODUCTS,
                        receipt=receipt_id, return_list=True)
        text += '\nAdded:'
        for rp in rps:
            text += '\n{}: {} {}'.format(rp['product_name'],
                                         rp['quantity'], rp['product_units'])
        products_page = db.get_page(db.PRODUCTS)
        receipt = db.get(db.RECEIPTS, id=receipt_id)
        if receipt['from_department']:
            dep_id = receipt['from_department']
            remainings = db.filter(db.INVENTORY_SUMMARY,
                                   department=dep_id, return_list=True)
            reply_markup = kb_add_product(
                master, products_page, receipt_id, 1, remainings)
        else:
            reply_markup = kb_add_product(
                master, products_page, receipt_id, 1)
        return await message.answer(text=text, reply_markup=reply_markup)
    else:
        return await message.answer('Enter a number\n If product was selected incorrectly, enter 0')


@dp.message_handler(state=Receipt.Create.note)
async def create_note(message: Message, state: FSMContext):
    data = await state.get_data()
    receipt_id = data['receipt_id']
    master_id = data['master_id']
    master = db.get(db.PROFILES, id=master_id)
    receipt = db.get(db.RECEIPTS, id=receipt_id)
    department = receipt['to_department'] if receipt['to_department'] else receipt['from_department']
    text = "Receipt created"
    reply_markup = kb_back_to_receipts(master, receipt_id, department)
    if message.text != 'Skip':
        db.edit_patch(
            db.RECEIPTS,
            receipt_id, note=message.text,
            requester=message.chat.id)
    return await message.answer(text=text, reply_markup=reply_markup)


@dp.callback_query_handler(cb.generic.filter(state=Receipt.Edit.DELETE), state='*')
async def delete_receipt(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    receipt_id = callback_data['data']
    products = db.filter(db.RECEIPT_PRODUCTS, receipt=receipt_id)
    products = [products] if not isinstance(products, list) else products
    text = ''
    for each in products:
        local_response = db.delete(
            db.RECEIPT_PRODUCTS, id=each['id'], requester=callback_query.message.chat.id)
        try:
            if local_response.json()['error'][0] == "Can't delete non-latest Receipt Product":
                text = 'Can\'t delete receipt that is not latest and contains products'
        except:
            pass
    if not text:
        response = db.delete(
            db.RECEIPTS,
            id=receipt_id,
            requester=callback_query.message.chat.id,
            raise_error=False)
        if response.status_code == 204:
            text = 'Receipt successfully deleted'
        elif response.status_code == 403:
            text = 'Not enough permissions to delete.'
        else:
            logging.error('⭕Error during deleting receipt')
            text = 'Error during deleting receipt'
    reply_markup = get_back(RECEIPTS)
    cb_add_data = {
        'state': Receipt.Create.INIT,
        'action': Receipt.Create.INIT,
        'data': '',
    }
    reply_markup.add(InlineKeyboardButton(
        'add new receipt', callback_data=cb.generic.new(**cb_add_data)))
    return await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=text,
        reply_markup=reply_markup
    )
