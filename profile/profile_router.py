from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile, FSInputFile
import os, asyncio, aiohttp
from io import BytesIO

from profile.create_img import create_profile_image
from db.CRUD import get_user_info_by_id


CURS = 88


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





pro_router = Router()

but1 = InlineKeyboardButton(text = "👁️ Скрыть аккаунт", callback_data="inviz")
but2 = InlineKeyboardButton(text = "↩️ Вывести", callback_data="output_money")
but3 = InlineKeyboardButton(text = "📊 Статистика", callback_data="stat")
but4 = InlineKeyboardButton(text = "📄 История Выводов", callback_data="hitory_output_miney")
but5 = InlineKeyboardButton(text = "↩️ Вернуться в главное меню", callback_data="menu")

profile_keyboard = InlineKeyboardMarkup(inline_keyboard = [[but1, but2], [but3, but4], [but5]])


@pro_router.message(F.text == "👦 Профиль")
async def pro_handler(message: types.Message):
    user = await get_user_info_by_id(message.from_user.id)
    data = {
        "id": message.from_user.id,
        "name": message.from_user.first_name,
        "money": user.money,
        "rang": "Senior",
        "lids": user.lids,
    }

    image_path = create_profile_image(data)  # Предполагаем, что это возвращает путь к файлу
    # print(image_path)
    # Использование функции в обработчике
    await message.answer_photo(photo = FSInputFile(image_path), reply_markup=profile_keyboard)







