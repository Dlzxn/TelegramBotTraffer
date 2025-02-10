from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from logs.loger_cfg import logger
from db.CRUD import get_all_myoffers, get_myoffer_by_id, get_session, add_url_to_offer, get_user_info_by_id
from admin.keyboard.key_admin import admin_keyboard

get_offers_router = Router()

# Константы для пагинации
OFFERS_PER_PAGE = 8
ITEMS_PER_ROW = 4


async def generate_offers_keyboard(page: int = 1):
    async with get_session()() as session:
        all_offers = await get_all_myoffers(session)

    # Фильтрация офферов (ваш текущий фильтр)
    filtered_offers = [offer for offer in all_offers if offer.user_id != "" and offer.url is None]

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
            callback_data=f"offer_detail_{offer.id}_{page}"
        )

    # Форматируем в два ряда по 4 кнопки
    builder.adjust(ITEMS_PER_ROW, ITEMS_PER_ROW)

    # Добавляем кнопки пагинации
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="← Назад",
                callback_data=f"offers_page_{page - 1}"
            )
        )
    if page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="Вперед →",
                callback_data=f"offers_page_{page + 1}"
            )
        )

    if pagination_buttons:
        builder.row(*pagination_buttons)

    # Кнопка возврата в главное меню
    builder.row(InlineKeyboardButton(
        text="Главное меню",
        callback_data="main_menu"
    ))

    return builder.as_markup()


@get_offers_router.callback_query(F.data.startswith("offers_page_"))
async def handle_offers_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    keyboard = await generate_offers_keyboard(page)
    await callback.message.edit_reply_markup(reply_markup=keyboard)


@get_offers_router.callback_query(F.data == "give_me_url")
async def show_offers(callback: CallbackQuery):
    keyboard = await generate_offers_keyboard()
    await callback.message.edit_text(
        "Список доступных офферов:",
        reply_markup=keyboard
    )

@get_offers_router.callback_query(F.data.startswith("main_menu"))
async def main_menu(callback: CallbackQuery):
    await callback.message.edit_text(text = "Выберите действие:", reply_markup=admin_keyboard)


@get_offers_router.callback_query(F.data.startswith("offer_detail_"))
async def show_offer_detail(callback: CallbackQuery):
    data = callback.data.split("_")
    offer_id = int(data[2])
    print("OFFER ID STR 87:", offer_id)
    page = int(data[3])

    # Получаем информацию о оффере из БД
    async with get_session()() as session:
        offer = await get_myoffer_by_id(session, offer_id)

    offer = offer[0]

    # Создаем клавиатуру для детального просмотра
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="↩Вернуться к списку",
            callback_data=f"offers_page_{page}"
        ),
        InlineKeyboardButton(
            text="🔗Добавить ссылку",
            callback_data=f"add_url_{offer_id}"
        )
    )
    builder.adjust(2)

    # Формируем текст сообщения (добавьте нужные поля из вашей модели)
    print("ОФФЕР ДЛЯ ЮРЛ:", offer.id)
    url_users = ""
    for x in offer.user_id.split():
        async with get_session()() as session:
            user = await get_user_info_by_id(session, int(x))
            logger.info(f"Пользователь {user}")
            try:
                url_users += f"@{user.username} "
            except Exception as e:
                logger.error(e)

    message_text = (
        f"📃Детальная информация по офферу {offer.id}:\n\n"
        f"⌨Название кнопки: {offer.button_name}\n"
        f"📦Название: {offer.name}\n"
        f"📄Комментарий: {offer.commentary}\n\n"
        f"👤Пользователи: {url_users}"
    )

    await callback.message.edit_text(
        message_text,
        reply_markup=builder.as_markup()
    )


class AddUrl(StatesGroup):
    id = 1
    url = State()

@get_offers_router.callback_query(F.data.startswith("add_url_"))
async def handle_add_url(callback: CallbackQuery, state: FSMContext):
    offer_id = int(callback.data.split("_")[2])
    # Ваша логика обработки добавления ссылки
    await callback.answer(f"Добавление ссылки для оффера {offer_id}\n"
                          f"Введите ссылку в строку сообщений:")
    await state.set_state(AddUrl.url)
    await state.update_data(id = offer_id)


@get_offers_router.message(AddUrl.url)
async def rename(message: Message, state: FSMContext):
    await state.update_data(url = message.text)
    data = await state.get_data()
    logger.info(f"Обновление ссылки для id{data["id"]} ссылка: {data["url"]}")
    await state.clear()
    async with get_session()() as session:
        new_offer = await add_url_to_offer(session, data["id"], data["url"])
    if new_offer:
        keyboard = await generate_offers_keyboard()
        await message.answer("Успешно сохранено", reply_markup=keyboard)


