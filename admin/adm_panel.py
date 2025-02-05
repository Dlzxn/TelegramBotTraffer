from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.CRUD import create_offer, get_session
from admin.keyboard.key_admin import admin_keyboard, offer_keyboard

# Определение состояния для создания оффера
class CreateOffer(StatesGroup):
    name = State()
    money = State()
    action = State()
    commentary = State()
    geo = State()

# Роутер для обработки команд администратора
admin_router = Router()


main_admins = ["Tashlinskiy", "illgettomorow"]

# Хендлер команды /admin
@admin_router.message(Command(commands=["admin"]))
async def admin(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=admin_keyboard)


# Хендлер нажатия кнопки "Создать оффер"
@admin_router.callback_query(F.data == "create_offer")
async def create_offers(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите название оффера:")
    await state.set_state(CreateOffer.name)
    await callback_query.answer()


@admin_router.callback_query(F.data == "adm_offer")
async def adm_offer(callback_query: types.CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=offer_keyboard)





# Хендлер для ввода названия оффера
@admin_router.message(CreateOffer.name)
async def set_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите сумму оффера (число):")
    await state.set_state(CreateOffer.money)


# Хендлер для ввода суммы оффера
@admin_router.message(CreateOffer.money)
async def set_money(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректное число:")
        return
    await state.update_data(money=int(message.text))
    await message.answer("Введите действие оффера:")
    await state.set_state(CreateOffer.action)


# Хендлер для ввода действия оффера
@admin_router.message(CreateOffer.action)
async def set_action(message: types.Message, state: FSMContext):
    await state.update_data(action=message.text)
    await message.answer("Введите комментарий к офферу (или пропустите, отправив 'нет'):")
    await state.set_state(CreateOffer.commentary)


# Хендлер для ввода комментария оффера
@admin_router.message(CreateOffer.commentary)
async def set_commentary(message: types.Message, state: FSMContext):
    commentary = message.text if message.text.lower() != "нет" else None
    await state.update_data(commentary=commentary)
    await message.answer("Введите географию оффера (например, RU, US, EU):")
    await state.set_state(CreateOffer.geo)


# Хендлер для ввода географии оффера
@admin_router.message(CreateOffer.geo)
async def set_geo(message: types.Message, state: FSMContext):
    await state.update_data(geo=message.text)
    data = await state.get_data()  # Получение всех данных
    await message.answer(
        f"Оффер создан:\n"
        f"Название: {data['name']}\n"
        f"Сумма: {data['money']}\n"
        f"Действие: {data['action']}\n"
        f"Комментарий: {data['commentary'] or 'Нет'}\n"
        f"География: {data['geo']}"
    )
    async with get_session()() as session:
        await create_offer(session, data["name"], data["money"], data["action"], data["geo"], data["commentary"])
    await state.clear()  # Очистка состояния







