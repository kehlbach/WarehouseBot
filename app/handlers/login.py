from aiogram import types
from aiogram.dispatcher import FSMContext

from app.data import callbacks as cb
from app.data.states import Login
from app.keyboards.menu import get_main_menu, kb_check_status, kb_send_number
from app.loader import bot, db, dp
from app.utils import tools
from app.utils.processors import name_validator, number_preprocessor


def WELCOME(master):
    return "Welcome.\n" + "Your role is - " + master["role_name"]


def _prepare_menu(master):
    permissions = tools.permissions(master)
    if master and any(permissions.values()):
        text = "Welcome.\n" + "Your role is - " + master["role_name"]
        reply_markup = get_main_menu(master)
    elif master:
        text = "Role is not set yet"
        reply_markup = kb_check_status
    else:
        text = "You are not registered.\n" + "/start to register"
        reply_markup = None
    return {"text": text, "reply_markup": reply_markup}


@dp.message_handler(commands="start", state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    """
    Conversation's entry point
    """
    await state.finish()
    user_id = message.from_id

    profile = db.filter(db.PROFILES, user_id=user_id)
    if profile and profile["name"]:
        await message.answer(**_prepare_menu(profile))
    elif profile:
        await Login.name.set()
        data = {"id": profile["id"]}
        await state.set_data(data)
        text = "Enter your name.\nExample:\n John Smith"
        return await message.answer(text)
    else:
        await Login.number.set()
        return await message.answer(
            "Share your phone number .", reply_markup=kb_send_number
        )


@dp.message_handler(state=Login.number, content_types=types.ContentType.CONTACT)
async def process_number(message: types.Message, state: FSMContext):
    formatted_number, is_valid, error_text = number_preprocessor(
        message=message, login=True
    )
    if not is_valid:
        return await message.answer(error_text)
    profile = db.filter(db.PROFILES, phone_number=formatted_number)
    if profile:
        if profile["name"]:
            await state.finish()
            profile = db.edit_patch(db.PROFILES, profile["id"], user_id=message.from_id)
            return await message.answer(**_prepare_menu(profile))
    else:
        admin_number = number_preprocessor(login=False)[0]
        if formatted_number == admin_number:
            role = db.filter(db.ROLES, name="Admin")["id"]
        else:
            role = db.filter(db.ROLES, name="No permissions")["id"]
        profile = db.add(
            db.PROFILES,
            phone_number=formatted_number,
            role=role,
            user_id=message.from_id,
        )
    data = {"id": profile["id"]}
    await state.set_data(data)
    await Login.name.set()
    text = "Enter your name.\nExample:\n John Smith"
    return await message.answer(text)


@dp.message_handler(state=Login.name)
async def process_name(message: types.Message, state: FSMContext):
    name, is_valid, error_text = name_validator(message.text)
    if not is_valid:
        return await message.answer(error_text)
    data = await state.get_data()
    profile = db.edit_patch(
        db.PROFILES, id=data["id"], name=name, user_id=message.from_id
    )
    await state.finish()
    return await message.answer(**_prepare_menu(profile))


@dp.callback_query_handler(cb.action.filter(action=Login.CHECK), state="*")
async def check_status(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query["from"]["id"]
    profile = db.filter(db.PROFILES, user_id=user_id)
    await state.finish()
    menu = _prepare_menu(profile)
    if menu["reply_markup"] == callback_query.message.reply_markup:
        await callback_query.answer("Your role is not set yet")
    else:
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text=menu["text"],
            reply_markup=menu["reply_markup"],
        )
