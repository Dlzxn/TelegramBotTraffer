from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile, FSInputFile, CallbackQuery
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import os, asyncio, aiohttp
from io import BytesIO

from profile.create_img import create_profile_image
from db.CRUD import get_user_info_by_id, get_tickets_by_user, get_all_users, update_user_privacy
from db.create_database import get_session

CURS = 88
TOP_USERS = []


async def usd_to_rub():
    url = "https://api.exchangerate-api.com/v4/latest/USD"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                # Пример: Возвращаем курс доллара к рублю
                rate = data['rates']['RUB']
                print(rate)
                global CURS
                CURS = rate
                await asyncio.sleep(500)
                await usd_to_rub()
            else:
                raise Exception("Error fetching exchange rate")
                await asyncio.sleep(500)
                await usd_to_rub()


def status(money_out: int | str) -> str:
    mon = int(money_out) / CURS
    status: str = None
    if mon > 0 and mon < 1000:
        return "Discipe"

    if mon > 1000 and mon < 2500:
        return "Averaged"

    if mon > 2500 and mon < 5000:
        return "Medium"

    if mon > 5000 and mon < 10000:
        return "Professional"

    if mon > 10000 and mon < 25000:
        return "TOP Highly"

    if  mon > 25000:
        return "Dominions Highly"






pro_router = Router()

but2 = InlineKeyboardButton(text = "↩️ Вывести", callback_data="output_money")
but3 = InlineKeyboardButton(text = "📊 Статистика", callback_data="stat")
but4 = InlineKeyboardButton(text = "📄 История Выводов", callback_data="hitory_output_money")
but5 = InlineKeyboardButton(text = "↩️ Вернуться в главное меню", callback_data="menu")


@pro_router.message(F.text == "👦 Профиль")
async def pro_handler(message: types.Message):
    async with get_session()() as session:
        user = await get_user_info_by_id(session, message.from_user.id)
    data = {
        "id": message.from_user.id,
        "name": message.from_user.first_name,
        "money": user.money,
        "rang": status(user.pay_out),
        "lids": user.lids,
    }
    if user.is_private:
        but1 = InlineKeyboardButton(text="👁️ Раскрыть аккаунт", callback_data="inviz")

    else:
        but1 = InlineKeyboardButton(text="👁 Скрыть аккаунт", callback_data="inviz")

    profile_keyboard = InlineKeyboardMarkup(inline_keyboard=[[but1, but2], [but3, but4], [but5]])

    image_path = create_profile_image(data)  # Предполагаем, что это возвращает путь к файлу
    # print(image_path)
    # Использование функции в обработчике
    await message.answer_photo(photo = FSInputFile(image_path), reply_markup=profile_keyboard)

@pro_router.callback_query(lambda c: c.data == "inviz")
async def inviz(c: CallbackQuery):
    async with get_session()() as session:
        user = await get_user_info_by_id(session, c.from_user.id)
    async with get_session()() as session:
        await update_user_privacy(session, c.from_user.id, user.is_private)
    async with get_session()() as session:
        user = await get_user_info_by_id(session, c.from_user.id)
        data = {
        "id": c.from_user.id,
        "name": c.from_user.first_name,
        "money": user.money,
        "rang": status(user.pay_out),
        "lids": user.lids,
    }
    if user.is_private:
        but1 = InlineKeyboardButton(text="👁️ Раскрыть аккаунт", callback_data="inviz")

    else:
        but1 = InlineKeyboardButton(text="👁 Скрыть аккаунт", callback_data="inviz")

    profile_keyboard = InlineKeyboardMarkup(inline_keyboard=[[but1, but2], [but3, but4], [but5]])
    await c.message.edit_reply_markup(reply_markup=profile_keyboard)

    await c.message.answer("🚨Настройки приватности успешно обновлены")



def generate_pagination_keyboard(current_index: int, total: int):
    builder = InlineKeyboardBuilder()

    # Кнопки быстрого перехода
    if total > 5:
        buttons = [
            InlineKeyboardButton(
                text=str(i + 1) if abs(i - current_index) > 2 else f"• {i + 1} •",
                callback_data=f"hpage_{i}"
            ) for i in range(max(0, current_index - 2), min(total, current_index + 3))
        ]
        builder.row(*buttons)

    # Основная навигация
    nav_buttons = []
    if current_index > 0:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=f"hpage_{current_index - 1}"
        ))

    nav_buttons.append(InlineKeyboardButton(
        text=f"{current_index + 1}/{total}",
        callback_data="ignore"
    ))

    if current_index < total - 1:
        nav_buttons.append(InlineKeyboardButton(
            text="➡️",
            callback_data=f"hpage_{current_index + 1}"
        ))

    builder.row(*nav_buttons)
    builder.row(InlineKeyboardButton(
        text="✖️ Закрыть",
        callback_data="close_history"
    ))

    return builder.as_markup()


@pro_router.callback_query(lambda c: c.data == "hitory_output_money")
async def show_first_output(c: CallbackQuery, state: FSMContext):
    tickets = await get_tickets_by_user(get_session(), c.from_user.id)

    if not tickets:
        await c.answer("❗ У вас еще нет выводов!")
        return

    # Отправляем новое сообщение вместо редактирования
    message = await c.message.answer(
        text=format_output_text(tickets[0], c.from_user, 0, len(tickets)),
        reply_markup=generate_pagination_keyboard(0, len(tickets))
    )

    # Сохраняем ID сообщения для последующего редактирования
    await state.update_data(history_message_id=message.message_id)
    await c.answer()




@pro_router.callback_query(lambda c: c.data.startswith("hpage_"))
async def handle_page_change(
        c: CallbackQuery,
        state: FSMContext,
        bot: Bot  # Добавляем инъекцию зависимости
):
    data = await state.get_data()
    message_id = data.get("history_message_id")

    if not message_id:
        await c.answer("❌ Сессия просмотра устарела")
        return

    page = int(c.data.split("_")[1])
    tickets = await get_tickets_by_user(get_session(), c.from_user.id)

    if not 0 <= page < len(tickets):
        await c.answer("❌ Неверная страница")
        return

    try:
        # Теперь bot доступен через инъекцию зависимости
        await bot.edit_message_text(
            chat_id=c.message.chat.id,
            message_id=message_id,
            text=format_output_text(tickets[page], c.from_user, page, len(tickets)),
            reply_markup=generate_pagination_keyboard(page, len(tickets))
        )
    except TelegramBadRequest as e:
        if "message to edit not found" in str(e):
            await c.answer("❌ Время сессии истекло, запросите историю заново")

    await c.answer()

@pro_router.callback_query(lambda c: c.data == "close_history")
async def close_history(c: CallbackQuery):
    await c.message.delete()
    await c.answer()


def format_output_text(ticket, user, current_index, total):
    return (
        f"📋 Вывод {current_index + 1} из {total}\n\n"
        f"🆔 Номер: {ticket.id}\n"
        f"⏰ Время: {ticket.time_created}\n"
        f"👤 Пользователь: {user.username}\n"
        f"💸 Сумма: {ticket.money_out}RUB\n"
        f"🏦 Способ: {ticket.bank}\n"
        f"📝 Комментарий: {ticket.commentary}\n"
        f"📌 Статус: {ticket.status}\n\n"
        f"Используйте кнопки ниже для навигации"
    )

async def top_users():
    await asyncio.sleep(5)
    async with get_session()() as session:  # Теперь создаем сессию через get_session()()
        users = await get_all_users(session)  #
    print(users)
    sort_users = sorted(users, key=lambda user: user.pay_out, reverse=True)
    print(list(sort_users))
    global TOP_USERS
    TOP_USERS = []
    for i in range(min(10, len(sort_users))):
        TOP_USERS.append(sort_users[i])

    await asyncio.sleep(100)
    await top_users()


@pro_router.callback_query(lambda c: c.data == "stat")
async def stat_handler(c: CallbackQuery):
    global TOP_USERS
    message = ""
    index = 1
    for user in TOP_USERS:
        print("PRIVAAAT", user.is_private)
        if not user.is_private:
            # Формируем правильную ссылку с экранированием только спецсимволов
            user_url = f"@{user.username}"
            message += f"{index}. {user_url}\nСумма вывода: {user.pay_out} RUB\n\n"
        else:
            message += f"{index}. Анонимный пользователь\nСумма вывода: {user.pay_out} RUB\n\n"
        index += 1

    # Экранируем специальные символы в тексте для MarkdownV2
    escaped_message = message

    # Отправляем сообщение
    await c.message.reply(
        text=f"ТОП ПОЛЬЗОВАТЕЛЕЙ:\n{escaped_message}"
    )
