from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile, FSInputFile, CallbackQuery
import os, asyncio, aiohttp
from io import BytesIO

from profile.create_img import create_profile_image
from db.CRUD import get_user_info_by_id, get_tickets_by_user, get_all_users
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

but1 = InlineKeyboardButton(text = "👁️ Скрыть аккаунт", callback_data="inviz")
but2 = InlineKeyboardButton(text = "↩️ Вывести", callback_data="output_money")
but3 = InlineKeyboardButton(text = "📊 Статистика", callback_data="stat")
but4 = InlineKeyboardButton(text = "📄 История Выводов", callback_data="hitory_output_money")
but5 = InlineKeyboardButton(text = "↩️ Вернуться в главное меню", callback_data="menu")

profile_keyboard = InlineKeyboardMarkup(inline_keyboard = [[but1, but2], [but3, but4], [but5]])


@pro_router.message(F.text == "👦 Профиль")
async def pro_handler(message: types.Message):
    user = await get_user_info_by_id(get_session(), message.from_user.id)
    data = {
        "id": message.from_user.id,
        "name": message.from_user.first_name,
        "money": user.money,
        "rang": status(user.pay_out),
        "lids": user.lids,
    }

    image_path = create_profile_image(data)  # Предполагаем, что это возвращает путь к файлу
    # print(image_path)
    # Использование функции в обработчике
    await message.answer_photo(photo = FSInputFile(image_path), reply_markup=profile_keyboard)



@pro_router.callback_query(lambda c: c.data == "hitory_output_money")
async def output_money_handler(c: CallbackQuery):
    tickets = await get_tickets_by_user(get_session(), c.from_user.id)
    text = ""
    for ticket in tickets:
        text += (f"Номер заявки: {ticket.id}\nВремя: {ticket.time_created}\nПользователь: {c.from_user.username}\n\n"
                 f"Сумма: {ticket.money_out}\nСпособ: {ticket.bank}\nКомментарий: {ticket.commentary}\n\nСтатус: {ticket.status}\n\n")
    await c.message.answer(text = f"Все ваши выводы: \n\n"
                   f"{text}")


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
        message += f"{index}. {user.username}\n Сумма вывода: {user.money}RUB\n\n"
        index += 1
    await c.message.reply(text = f"ТОП ПОЛЬЗОВАТЕЛЕЙ:\n"
                                 f"{message}")














