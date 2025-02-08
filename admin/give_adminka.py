from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from admin.adm_panel import main_admins
from db.CRUD import get_session, get_user_info_by_id, update_user_admin_status, get_user_by_username
from admin.keyboard.key_admin import admin_keyboard

admin_router_adm = Router()


class AdminState(StatesGroup):
    waiting_for_user = State()


async def generate_admin_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Выдать права", callback_data="give_admin")],
            [InlineKeyboardButton(text="Забрать права", callback_data="remove_admin")],
            [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
        ]
    )
    return keyboard


@admin_router_adm.callback_query(F.data == "adm_prava")
async def main_menu(callback: CallbackQuery):
    if callback.from_user.username in main_admins:
        await callback.message.edit_text("Выберите действие:", reply_markup=await generate_admin_keyboard())
    else:
        await callback.message.edit_text(text = "Доступ запрещен",
                                      reply_markup=InlineKeyboardMarkup(inline_keyboard=
                                         [[InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]]))


@admin_router_adm.callback_query(F.data.in_(["give_admin", "remove_admin"]))
async def ask_for_user(callback: CallbackQuery, state: FSMContext):
    action = "выдать" if callback.data == "give_admin" else "забрать"
    await state.set_state(AdminState.waiting_for_user)
    await state.update_data(action=callback.data)
    await callback.message.answer(
        f"Введите @username или ID пользователя, которому хотите {action} права администратора.")


@admin_router_adm.message(AdminState.waiting_for_user)
async def process_admin_action(message: Message, state: FSMContext):
    user_input = message.text.strip()
    data = await state.get_data()
    action = data["action"]

    async with get_session()() as session:
        id_user = await get_user_by_username(session, message.text)
        user = await get_user_info_by_id(session, id_user.telegram_id)

        if not user:
            await message.answer("Пользователь не найден или не является участником бота.")
            return

        new_status = not user.is_admin
        await update_user_admin_status(session, user.telegram_id, new_status)
        await message.answer(
            f"Права администратора {'выданы' if new_status else 'забраны'} у пользователя {user.username or user.telegram_id}.")

    await state.clear()
