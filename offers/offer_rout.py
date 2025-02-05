from aiogram import Router, F
from aiogram.types import (PollAnswer, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup,
                           Message, CallbackQuery)


from db.CRUD import get_offers_by_user_id, get_session, get_all_offers, assign_user_to_offer


but1 = InlineKeyboardButton(text = "🔍 Все офферы", callback_data = "all_offers")
but2 = InlineKeyboardButton(text = "💼 Мои офферы", callback_data = "my_offers")
but3 = InlineKeyboardButton(text = "↩️ Вернуться в главное меню", callback_data= "menu")

project_keyboard = InlineKeyboardMarkup(inline_keyboard = [[but2, but1], [but3]])

offers_rout = Router()

@offers_rout.message(F.text == "📦 Офферы")
async def offer(message: Message):
    await message.reply(text = "Выберите следующий пункт в меню", reply_markup = project_keyboard)

@offers_rout.callback_query(lambda c: c.data == "my_offers")
async def my_offers(c: CallbackQuery):
    async with get_session()() as session:
        my_offers = await get_offers_by_user_id(session, c.from_user.id)
    if len(my_offers) == 0:
        await c.message.answer("У вас нет активных офферов")
    else:
        for offer in my_offers:
            response_text = (
                f"📌 Оффер #{offer.id}\n\n"
                f"🏷 Название: {offer.name}\n"
                f"⚒️ Действие: {offer.action}\n"
                f"📝 Описание: {offer.commentary}\n"
                f"💵 Цена: {offer.money}\n"
                f"🌍 GEO: {offer.geo}\n\n\n"
                f"📅 Ссылка: {offer.url}\n"
            )
            await c.message.answer(response_text)


from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.CRUD import get_offer_by_id  # Убедитесь, что эта функция существует в CRUD

# Добавим кнопку "Назад" для возврата в меню офферов
back_to_offers_button = InlineKeyboardButton(text="↩️ Назад", callback_data="all_offers_back")


def generate_offers_keyboard(offers, page=0, per_page=6):
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки офферов
    start_idx = page * per_page
    text = ""
    for offer in offers[start_idx:start_idx + per_page]:
        print("OFFER", offer.id)
        builder.button(
            text=f"{offer.button_name}",
            callback_data=f"offer_details_{offer.id}"
        )
        text += f"{offer.button_name}-{offer.name}-{offer.money}\n"

    # Добавляем кнопки пагинации
    total_pages = (len(offers) + per_page - 1) // per_page
    if total_pages > 1:
        if page > 0:
            builder.button(text="⬅️ Назад", callback_data=f"all_offers_page_{page - 1}")
        if page < total_pages - 1:
            builder.button(text="Вперед ➡️", callback_data=f"all_offers_page_{page + 1}")

    # Добавляем кнопку возврата
    builder.button(text="↩️ Назад", callback_data="all_offers_back")

    return builder.adjust(1, 2, 1).as_markup(), text


@offers_rout.callback_query(F.data == "all_offers")
async def show_all_offers(c: CallbackQuery):
    async with get_session()() as session:
        all_offers = await get_all_offers(session)

    if not all_offers:
        await c.message.answer("Нет доступных офферов.")
        return

    keyboard, text = generate_offers_keyboard(all_offers)
    await c.message.edit_text(f" Все офферы (страница 1):\n{text}", reply_markup=keyboard)


@offers_rout.callback_query(F.data.startswith("all_offers_page_"))
async def handle_pagination(c: CallbackQuery):
    page = int(c.data.split("_")[-1])

    async with get_session()() as session:
        all_offers = await get_all_offers(session)

    total_pages = (len(all_offers) + 5) // 6
    if page < 0 or page >= total_pages:
        await c.answer("Это последняя страница")
        return

    keyboard, text = generate_offers_keyboard(all_offers, page)
    await c.message.edit_text(f"📦 Все офферы (страница {page + 1}):\n{text}", reply_markup=keyboard)


@offers_rout.callback_query(F.data.startswith("offer_details_"))
async def show_offer_details(c: CallbackQuery):
    offer_id = int(c.data.split("_")[-1])

    async with get_session()() as session:
        offers = await get_offer_by_id(session, offer_id)

    if not offers:
        await c.answer("Оффер больше не доступен")
        return
    print(f"OFFER LIST {offers[0].id}")
    offer = offers[0]

    response_text = (
        f"📌 Оффер #{offer.id}\n\n"
        f"🏷 Название: {offer.name}\n"
        f"⚒️ Действие: {offer.action}\n"
        f"📝 Описание: {offer.commentary}\n"
        f"💵 Цена: {offer.money}\n"
        f"🌍 GEO: {offer.geo}\n"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="↩️ К списку офферов", callback_data="all_offers")
    print(str(c.message.from_user.id), str(offer.user_id).split(), str(c.message.from_user.id) not in str(offer.user_id).split())
    if str(c.from_user.id) not in str(offer.user_id).split():
        builder.button(text="🎯 Взять оффер", callback_data=f"take_offer_{offer.id}")
    await c.message.edit_text(response_text, reply_markup=builder.as_markup())


@offers_rout.callback_query(F.data == "all_offers_back")
async def back_to_offers_menu(c: CallbackQuery):
    await c.message.edit_text("Выберите следующий пункт в меню", reply_markup=project_keyboard)


@offers_rout.callback_query(F.data.startswith("take_offer_"))
async def take_offer(c: CallbackQuery):
    offer_id = int(c.data.split("_")[-1])

    async with get_session()() as session:
        # Предполагаем, что assign_user_to_offer принимает user_id и offer_id
        user_id = c.from_user.id
        print(f"TAKE OFFER {offer_id}")
        result = await assign_user_to_offer(session, offer_id, user_id)

    if result:
        await c.message.answer("Вы успешно взяли оффер!")
    else:
        await c.message.answer("Не удалось взять оффер. Попробуйте снова.")

    # Возвращаем пользователя к списку офферов
    await c.message.edit_text("📦 Все офферы", reply_markup=project_keyboard)





