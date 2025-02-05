from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from admin.get_offers_fron_user import AddUrl
from logs.loger_cfg import logger
from db.CRUD import (get_all_offers, get_offer_by_id, get_session, add_url_to_offer, get_user_info_by_username,
                     assign_user_to_offer)
from admin.keyboard.key_admin import admin_keyboard

get_offers_router_to = Router()

# Константы для пагинации
OFFERS_PER_PAGE = 8
ITEMS_PER_ROW = 4


async def generate_offers_keyboard(page: int = 1):
    async with get_session()() as session:
        all_offers = await get_all_offers(session)

    # Фильтрация офферов
    filtered_offers = [offer for offer in all_offers]

    # Пагинация
    total_pages = (len(filtered_offers) + OFFERS_PER_PAGE - 1) // OFFERS_PER_PAGE
    start_idx = (page - 1) * OFFERS_PER_PAGE
    end_idx = start_idx + OFFERS_PER_PAGE
    current_offers = filtered_offers[start_idx:end_idx]

    builder = InlineKeyboardBuilder()

    # Добавляем кнопки с номерами офферов
    for offer in current_offers:
        builder.button(
            text=str(offer.id),
            callback_data=f"offer_url_detail_{offer.id}_{page}"
        )

    # Форматируем в два ряда по 4 кнопки
    builder.adjust(ITEMS_PER_ROW, ITEMS_PER_ROW)

    # Добавляем кнопки пагинации
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="← Назад",
                callback_data=f"ofers_page_{page - 1}"
            )
        )
    if page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="Вперед →",
                callback_data=f"ofers_page_{page + 1}"
            )
        )

    if pagination_buttons:
        builder.row(*pagination_buttons)

    # Кнопка возврата в главное меню
    builder.row(InlineKeyboardButton(
        text="Главное меню",
        callback_data="main_"
    ))

    return builder.as_markup()


@get_offers_router_to.callback_query(F.data.startswith("ofers_page_"))
async def handle_offers_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    keyboard = await generate_offers_keyboard(page)
    await callback.message.edit_reply_markup(reply_markup=keyboard)


@get_offers_router_to.callback_query(F.data == "user_take_offer")
async def show_offers(callback: CallbackQuery):
    keyboard = await generate_offers_keyboard()
    await callback.message.edit_text(
        "Список доступных офферов:",
        reply_markup=keyboard
    )


@get_offers_router_to.callback_query(F.data == "main_")
async def main_menu(callback: CallbackQuery):
    await callback.message.edit_text(text="Выберите действие:", reply_markup=admin_keyboard)


@get_offers_router_to.callback_query(F.data.startswith("offer_url_detail_"))
async def show_offer_detail(callback: CallbackQuery):
    data = callback.data.split("_")
    print("DATA STR 95", data)
    offer_id = int(data[3])
    page = int(data[4])

    # Получаем информацию о оффере из БД
    async with get_session()() as session:
        offer = await get_offer_by_id(session, offer_id)

    offer = offer[0]

    # Создаем клавиатуру для детального просмотра
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Вернуться к списку",
            callback_data=f"ofers_page_{page}"
        ),
        InlineKeyboardButton(
            text="Выдать юзеру",
            callback_data=f"give_offer_to_user_{offer.id}"
        )
    )
    builder.adjust(3)

    # Формируем текст сообщения (добавьте нужные поля из вашей модели)
    message_text = (
        f"Детальная информация по офферу {offer.id}:\n\n"
        f"Название кнопки: {offer.button_name}\n"
        f"Название: {offer.name}\n"
        f"Комментарий: {offer.commentary}\n\n"
        f"В работе: {offer.user_id}"
    )

    await callback.message.edit_text(
        message_text,
        reply_markup=builder.as_markup()
    )


class AddUser(StatesGroup):
    id = 1
    url = State()


@get_offers_router_to.callback_query(F.data.startswith("add_url_"))
async def handle_add_url(callback: CallbackQuery, state: FSMContext):
    offer_id = int(callback.data.split("_")[2])
    await callback.answer(f"Добавление ссылки для оффера {offer_id}\n"
                          f"Введите ссылку ниже:")
    await state.set_state(AddUrl.url)
    await state.update_data(id=offer_id)


@get_offers_router_to.message(AddUrl.url)
async def rename(message: Message, state: FSMContext):
    await state.update_data(url=message.text)
    data = await state.get_data()
    logger.info(f"Обновление ссылки для id {data['id']} ссылка: {data['url']}")
    await state.clear()
    async with get_session()() as session:
        new_offer = await add_url_to_offer(session, data["id"], data["url"])
    if new_offer:
        keyboard = await generate_offers_keyboard()
        await message.answer("Успешно сохранено", reply_markup=keyboard)


@get_offers_router_to.callback_query(F.data.startswith("give_offer_to_user_"))
async def give_offer_to_user(callback: CallbackQuery, state: FSMContext):
    offer_id = int(callback.data.split("_")[4])

    # Получаем информацию о оффере из БД
    async with get_session()() as session:
        offer = await get_offer_by_id(session, offer_id)
    offer = offer[0]

    # Попросим пользователя ввести свой юзернейм
    await callback.message.answer(f"Введите ваш юзернейм для получения оффера {offer.name}:")
    await state.set_state(AddUser.url)
    await state.update_data(id=offer.id)


@get_offers_router_to.message(AddUser.url)
async def handle_username_input(message: Message, state: FSMContext):
    # Получаем данные из состояния
    await state.update_data(url=message.text)
    data = await state.get_data()
    logger.info("Data: ", data["url"])
    offer_id = data["id"]

    # Отправляем запрос на добавление юзера к офферу в БД
    async with get_session()() as session:
        offer = await get_offer_by_id(session, offer_id)
        offer = offer[0]
        # Получаем пользователя
        user = await get_user_info_by_username(session, data["url"])

        if user:
            if str(user.id) in str(offer.user_id).split():
                await message.answer("Данный пользователь уже выполняет оффер")
            else:

                await message.answer(f"Оффер {offer.name} выдан пользователю {user.username}!")
        else:
            await assign_user_to_offer(session, data["id"], user.id)
            await message.answer(f"Пользователь с юзернеймом {username} не найден.")
        await state.clear()
