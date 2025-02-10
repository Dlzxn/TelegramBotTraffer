from aiogram import Router, types, F, Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup

from sqlalchemy.ext.asyncio import AsyncSession
from db.CRUD import (get_tickets_by_status, update_ticket_status, get_ticket_by_id, get_session,
                     update_plus_out_money, update_plus_money)
from logs.loger_cfg import logger

money_router = Router()

MenuCallback = CallbackData()

@money_router.callback_query(F.data.startswith("get_money"))
async def open_main_menu(callback: types.CallbackQuery):
    se1 = InlineKeyboardButton(text="📜 История выводов", callback_data="menu:history::")
    se2 = InlineKeyboardButton(text="⌛ Ожидают вывода", callback_data="menu:pending::")
    se3 = InlineKeyboardButton(text="🔙 Вернуться обратно", callback_data="main_menu")
    await callback.message.edit_text("💰 Главное меню:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[se1, se2], [se3]]))

@money_router.callback_query(F.data.startswith("menu:history"))
async def open_history_menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardBuilder()
    b1 = InlineKeyboardButton(text="✅ Подтвержденные", callback_data="menu:view:✅ Подтверждена:")
    b2 = InlineKeyboardButton(text="❌ Отклоненные", callback_data="menu:view:❌ Отклонена:")
    b3 = InlineKeyboardButton(text="🔙 Вернуться назад", callback_data="get_money")
    await callback.message.edit_text("📜 История выводов:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[b1, b2], [b3]]))


@money_router.callback_query(F.data.startswith("menu:view"))
async def view_tickets(callback: types.CallbackQuery):
    data_parts = callback.data.split(":")
    status = data_parts[2]
    current_page = int(data_parts[3]) if len(data_parts) > 3 and data_parts[3].isdigit() else 1

    async with get_session()() as session:
        all_tickets = await get_tickets_by_status(session, status)

    # Пагинация
    items_per_page = 6
    total_pages = (len(all_tickets) + items_per_page - 1) // items_per_page
    start_idx = (current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_tickets = all_tickets[start_idx:end_idx]

    keyboard = InlineKeyboardBuilder()

    # Кнопки заявок (максимум 6 в ряд)
    for ticket in page_tickets:
        keyboard.button(
            text=f"📌 {ticket.id}",
            callback_data=f"menu:details:{ticket.status}:{ticket.id}"
        )
    keyboard.adjust(6)  # 6 кнопок в ряд

    # Кнопки пагинации (только если есть несколько страниц)
    if total_pages > 1:
        pagination_row = InlineKeyboardBuilder()

        # Кнопка "Назад"
        prev_page = max(1, current_page - 1)
        pagination_row.button(
            text="◀️" if current_page > 1 else " ",
            callback_data=f"menu:view:{status}:{prev_page}" if current_page > 1 else "no_action"
        )

        # Номер страницы
        pagination_row.button(
            text=f"{current_page}/{total_pages}",
            callback_data="no_action"
        )

        # Кнопка "Вперед"
        next_page = min(total_pages, current_page + 1)
        pagination_row.button(
            text="▶️" if current_page < total_pages else " ",
            callback_data=f"menu:view:{status}:{next_page}" if current_page < total_pages else "no_action"
        )

        keyboard.attach(pagination_row)

    # Кнопка возврата
    keyboard.row(
        types.InlineKeyboardButton(
            text="🔙 Вернуться назад",
            callback_data="menu:history"
        )
    )

    await callback.message.edit_text(
        f"📋 Заявки ({status}) - Страница {current_page}:",
        reply_markup=keyboard.as_markup()
    )


@money_router.callback_query(F.data.startswith("menu:details"))
async def view_ticket_details(callback: types.CallbackQuery):
    data_parts = callback.data.split(":")
    async with get_session()() as session:
        ticket = await get_ticket_by_id(session, int(data_parts[3]))
    text = (f"💳 Заявка #{ticket.id}\n"
            f"👤 Пользователь: {ticket.id_user}\n"
            f"💰 Сумма: {ticket.money_out}₽\n"
            f"🏦 Банк: {ticket.bank}\n"
            f"🔢 Карта: {ticket.card_number}\n"
            f"📝 Комментарий: {ticket.commentary}\n"
            f"⏳ Дата создания: {ticket.time_created}\n"
            f"📌 Статус: {ticket.status}")

    await callback.message.edit_text(text, reply_markup=callback.message.reply_markup)

@money_router.callback_query(F.data.startswith("menu:pending"))
async def view_pending_tickets(callback: types.CallbackQuery):
    async with get_session()() as session:
        tickets = await get_tickets_by_status(session, "🕐 Создана")
    if not tickets:
        await callback.answer("Нет ожидающих заявок", show_alert=True)
        return
    ticket = tickets[0]
    await show_pending_ticket(callback, ticket)

async def show_pending_ticket(callback, ticket):
    text = (f"💳 Заявка #{ticket.id}\n"
            f"👤 Пользователь: {ticket.id_user}\n"
            f"💰 Сумма: {ticket.money_out}₽\n"
            f"🏦 Банк: {ticket.bank}\n"
            f"🔢 Карта: {ticket.card_number}\n"
            f"📝 Комментарий: {ticket.commentary}\n"
            f"⏳ Дата создания: {ticket.time_created}\n"
            f"📌 Статус: {ticket.status}")
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Подтвердить", callback_data=f"menu:approve:::{ticket.id}")
    keyboard.button(text="❌ Отклонить", callback_data=f"menu:reject:::{ticket.id}")
    keyboard.button(text="🔙 В меню", callback_data="get_money")
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

@money_router.callback_query(F.data.startswith("menu:approve"))
@money_router.callback_query(F.data.startswith("menu:reject"))
async def process_ticket(callback: types.CallbackQuery, bot: Bot):
    print(callback.data.split(":"))
    action, status, _, _,  ticket_id = callback.data.split(":")
    print(action + status)
    new_status = "✅ Подтверждена" if action + status == "menuapprove" else "❌ Отклонена"
    logger.info(f"Заявка {ticket_id} cо статусом {new_status}")

    # Получаем сессию с помощью async_sessionmaker

    # Работаем с сессией в блоке контекстного менеджера
    async with get_session()() as session:
        # Обновляем статус тикета
        await update_ticket_status(session, int(ticket_id), new_status)

        # После обновления статуса, отображаем обновленные тикеты
        await view_pending_tickets(callback)
    print(new_status, new_status == "✅ Подтверждена")

    if new_status == "✅ Подтверждена":
        print("В функции")
        async with get_session()() as session:
            ticket = await get_ticket_by_id(session, int(ticket_id))
            print("ID", callback.from_user.id)
            print("MONEY OUT", ticket.money_out)
            await update_plus_out_money(session, ticket.id_user, ticket.money_out)
            await update_plus_money(session, ticket.id_user, -ticket.money_out)
            await callback.message.answer("Вывод успешно подтвержден✍️")
            await bot.send_message(ticket.id_user, f"✅Ваша заявка на вывод №{ticket.id} успешно подтверждена")
    else:
        await callback.message.answer("Вывод успешно отклонен✏️")
        async with get_session()() as session:
            ticket = await get_ticket_by_id(session, int(ticket_id))
            await bot.send_message(ticket.id_user, f"❌Ваша заявка на вывод №{ticket.id} отклонена📌")