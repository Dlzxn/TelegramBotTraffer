from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm import state
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from logs.loger_cfg import logger
from db.CRUD import get_user_by_username, update_lids, update_money, update_ban_status, update_out_money
from db.create_database import get_session

router = Router()


# Функция для получения пользователя по никнейму

class RefUser(StatesGroup):
    username = State()

# Команда для поиска пользователя
@router.callback_query(F.data == "refact_profile")
async def edit_profile_command(c: CallbackQuery, state: FSMContext):
    await c.message.answer("Введите никнейм пользователя:")
    await state.set_state(RefUser.username)


@router.message(RefUser.username)
async def process_username(message: types.Message, state: FSMContext):
    await state.clear()
    async with get_session()() as session:
        user = await get_user_by_username(session, message.text)

    if not user:
        await message.answer("Пользователь не найден.")
        return

    # Формируем сообщение с информацией
    text = (f"👤 Пользователь: {user.username}\n"
            f"ID: {user.id}\n\n"
            f"📊 Лидов: {user.lids}\n"
            f"💳 Баланс: {user.money}\n"
            f"📤 Выведено денег: {user.pay_out}\n"
            f"🛡 Админка: {'Да' if user.is_admin else 'Нет'}\n"
            f"👁 Приватность{'Да' if user.is_private else 'Нет'}\n"
            f"🚫 Блокировка: {'Да' if user.is_ban else 'Нет'}")

    # Создаем клавиатуру
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="👥Изменить лидов", callback_data=f"edit_lids:{user.id}")
    keyboard.button(text="💲Изменить баланс", callback_data=f"edit_money:{user.id}")
    keyboard.button(text="💱Изменить баланс вывода", callback_data=f"edit_out:{user.id}")
    if not user.is_ban:
        keyboard.button(text="❌Заблокировать", callback_data=f"block_user:{user.id}")
    else:
        keyboard.button(text="✔Разблокировать", callback_data=f"unblock_user:{user.id}")
    keyboard.adjust(2)

    await message.answer(text, reply_markup=keyboard.as_markup())

class ReUsers(StatesGroup):
    id = State()
    lids = State()
    money = State()
    out_money = State()


# Обработчики для изменения данных
@router.callback_query(F.data.startswith("edit_lids:"))
async def edit_lids_callback(call: types.CallbackQuery, state: FSMContext):
    user_id = int(call.data.split(":")[1])
    await call.message.answer("Введите новое число подписчиков:")
    await state.update_data(user_id=user_id)
    await state.set_state(ReUsers.lids)
    await call.answer()


@router.message(ReUsers.lids)
async def process_lids_input(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]
    if not message.text.isdigit():
        await message.answer("Введите корректное число подписчиков.")
        return
    async with get_session()() as session:
        await update_lids(session, user_id, int(message.text))
    print(user_id, message.text)
    await message.answer("✅ Подписчики обновлены.")
    logger.info(f"У пользователя {user_id} обновлены лиды до {message.text}")
    await state.clear()



#деньги--------------------


# Обработчики для изменения данных
@router.callback_query(F.data.startswith("edit_money:"))
async def edit_lids_callback(call: types.CallbackQuery, state: FSMContext):
    user_id = int(call.data.split(":")[1])
    await call.message.answer("Введите новый баланс:")
    await state.update_data(user_id=user_id)
    await state.set_state(ReUsers.money)
    await call.answer()


@router.message(ReUsers.money)
async def process_lids_input(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]
    if not message.text.isdigit():
        await message.answer("Введите корректное число:")
        return
    async with get_session()() as session:
        await update_money(session, user_id, int(message.text))
    print(user_id, message.text)
    await message.answer("✅ Баланс обновлен.")
    logger.info(f"У пользователя {user_id} обновлен баланс до {message.text}")
    await state.clear()






#/////////////////////////------для выведенный денег


@router.callback_query(F.data.startswith("edit_out:"))
async def edit_lids_callback(call: types.CallbackQuery, state: FSMContext):
    user_id = int(call.data.split(":")[1])
    await call.message.answer("Введите новое количество выведенных денег:")
    await state.update_data(user_id=user_id)
    await state.set_state(ReUsers.out_money)
    await call.answer()


@router.message(ReUsers.out_money)
async def process_lids_input(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]
    if not message.text.isdigit():
        await message.answer("Введите корректное число:")
        return
    async with get_session()() as session:
        await update_out_money(session, user_id, int(message.text))
    print(user_id, message.text)
    await message.answer("✅ Баланс обновлен.")
    logger.info(f"У пользователя {user_id} обновлен баланс до {message.text}")
    await state.clear()


# Аналогично делаем для баланса и ранга

@router.callback_query(F.data.startswith("block_user:"))
async def block_user_callback(call: types.CallbackQuery):
    user_id = int(call.data.split(":")[1])
    async with get_session()() as session:
        await update_ban_status(session, user_id, True)
    await call.message.answer("🚫 Пользователь заблокирован.")
    await call.answer()


@router.callback_query(F.data.startswith("unblock_user:"))
async def unblock_user_callback(call: types.CallbackQuery):
    user_id = int(call.data.split(":")[1])
    async with get_session()() as session:
        await update_ban_status(session, user_id, False)
    await call.message.answer("✅ Пользователь разблокирован.")
    await call.answer()
