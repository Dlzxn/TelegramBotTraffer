from aiogram import Router
from aiogram import types, F
from aiogram.fsm import state
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm import state

from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.CRUD import (get_offer_by_id, get_session, get_all_offers, update_offer_name, delete_offer, update_offer_action,
                     update_offer_commentary, get_user_info_by_id)
from admin.keyboard.key_admin import admin_keyboard, offer_keyboard

adm_router_refact = Router()


# Добавим кнопку "Назад" для возврата в меню офферов
back_to_offers_button = InlineKeyboardButton(text="↩️ Назад", callback_data="all_offers_back")



def generate_offers_keyboard(offers, page=0, per_page=20):
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки офферов
    start_idx = page * per_page
    text = ""
    for offer in offers[start_idx:start_idx + per_page]:
        print("OFFER", offer.id)
        builder.button(
            text=f"{offer.button_name}",
            callback_data=f"adm_offer_details_{offer.id}"
        )
        text += f"{offer.button_name}-{offer.name}-{offer.money}\n"

    # Добавляем кнопки пагинации
    total_pages = (len(offers) + per_page - 1) // per_page
    if total_pages > 1:
        if page > 0:
            builder.button(text="⬅️ Назад", callback_data=f"adm_offers_page_{page - 1}")
        if page < total_pages - 1:
            builder.button(text="Вперед ➡️", callback_data=f"adm_offers_page_{page + 1}")

    # Добавляем кнопку возврата
    builder.button(text="↩️ Назад", callback_data="adm_offer_cancel")

    return builder.adjust(1, 2, 1).as_markup()


@adm_router_refact.callback_query(F.data == "adm_offer_cancel")
async def back_all_offers(c: CallbackQuery):
    await c.message.edit_text(text = "Выберите действие:", reply_markup=admin_keyboard)

@adm_router_refact.callback_query(F.data == "adm_offer_search")
async def show_all_offers(c: CallbackQuery):
    async with get_session()() as session:
        all_offers = await get_all_offers(session)

    if not all_offers:
        await c.message.answer("Нет доступных офферов.")
        return

    keyboard= generate_offers_keyboard(all_offers)
    await c.message.edit_text(f"Выберите оффер для изменений", reply_markup=keyboard)


@adm_router_refact.callback_query(F.data.startswith("adm_offers_page_"))
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


@adm_router_refact.callback_query(F.data.startswith("adm_offer_details_"))
async def show_offer_details(c: CallbackQuery):
    offer_id = int(c.data.split("_")[-1])

    async with get_session()() as session:
        offers = await get_offer_by_id(session, offer_id)

    if not offers:
        await c.answer("Оффер больше не доступен")
        return
    print(f"OFFER LIST {offers[0].id}")
    offer = offers[0]
    text_all_users = ""
    for id in offer.user_id.split():
        async with get_session()() as session:
            user = await get_user_info_by_id(session, int(id))
            text_all_users += f"@{user.username} "

    response_text = (
        f"📌 Оффер #{offer.id}\n\n"
        f"🏷 Название: {offer.name}\n"
        f"⚒️ Действие: {offer.action}\n"
        f"📝 Описание: {offer.commentary}\n"
        f"💵 Цена: {offer.money}\n"
        f"🌍 GEO: {offer.geo}\n\n"
        f"Выполняют {text_all_users}"
    )


    de1 = InlineKeyboardButton(text="↩️ К списку офферов", callback_data="adm_offer_search")
    de2 = InlineKeyboardButton(text="↩️ Изменить имя кнопки", callback_data=f"create_but_name_{offer_id}")
    de3 = InlineKeyboardButton(text="↩️ Изменить Текст", callback_data=f"refact_text_{offer_id}")
    de4 = InlineKeyboardButton(text="↩️ Изменить Описание", callback_data=f"refact_description_{offer_id}")
    de5 = InlineKeyboardButton(text="↩️ Удалить оффер", callback_data=f"delete_offer_{offer_id}")
    refact_keyboard = InlineKeyboardMarkup(inline_keyboard=[[de4, de2], [de3, de5], [de1]])
    print(str(c.message.from_user.id), str(offer.user_id).split(), str(c.message.from_user.id) not in str(offer.user_id).split())
    await c.message.edit_text(response_text, reply_markup=refact_keyboard)

class Rename(StatesGroup):
    id = 0
    name = State()

@adm_router_refact.callback_query(F.data.startswith("create_but_name_"))
async def create_name_offer(c: CallbackQuery, state: FSMContext):
    offer_id = int(c.data.split("_")[-1])
    await c.message.answer("Введите новое название")
    await state.set_state(Rename.name)
    await state.update_data(id=offer_id)

@adm_router_refact.message(Rename.name)
async def rename(message: Message, state: FSMContext):
    await state.update_data(name = message.text)
    data = await state.get_data()
    await state.clear()
    async with get_session()() as session:
        new_offer = await update_offer_name(session, data["id"], data["name"])
    if new_offer:
        await message.answer("Успешно сохранено", reply_markup=offer_keyboard)


@adm_router_refact.callback_query(F.data.startswith("delete_offer_"))
async def create_name_offer(c: CallbackQuery):
    offer_id = int(c.data.split("_")[-1])
    async with get_session()() as session:
        status = await delete_offer(session, offer_id)
    if status:
        await c.message.answer("Оффер успешно удален!", reply_markup=offer_keyboard)

class ReText(StatesGroup):
    id = 0
    name = State()

@adm_router_refact.callback_query(F.data.startswith("refact_text_"))
async def create_name_offer(c: CallbackQuery, state: FSMContext):
    offer_id = int(c.data.split("_")[-1])
    await c.message.answer("Введите новый текст")
    await state.set_state(ReText.name)
    await state.update_data(id=offer_id)

@adm_router_refact.message(ReText.name)
async def rename(message: Message, state: FSMContext):
    await state.update_data(name = message.text)
    data = await state.get_data()
    await state.clear()
    async with get_session()() as session:
        new_offer = await update_offer_action(session, data["id"], data["name"])
    if new_offer:
        await message.answer("Успешно сохранено", reply_markup=offer_keyboard)


class ReDescription(StatesGroup):
    id = 0
    name = State()

@adm_router_refact.callback_query(F.data.startswith("refact_description_"))
async def create_name_offer(c: CallbackQuery, state: FSMContext):
    offer_id = int(c.data.split("_")[-1])
    await c.message.answer("Введите новый текст")
    await state.set_state(ReDescription.name)
    await state.update_data(id=offer_id)

@adm_router_refact.message(ReDescription.name)
async def rename(message: Message, state: FSMContext):
    await state.update_data(name = message.text)
    data = await state.get_data()
    await state.clear()
    async with get_session()() as session:
        new_offer = await update_offer_commentary(session, data["id"], data["name"])
    if new_offer:
        await message.answer("Успешно сохранено", reply_markup=offer_keyboard)