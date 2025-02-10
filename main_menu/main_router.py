from aiogram import Router, F
from aiogram import types
from aiogram.types import PollAnswer
from aiogram.types import PollAnswer, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import asyncio

from logs.loger_cfg import logger
from text.all_texts import info_text, manual_url, navigation_url


all_command: list = ["📌 О проекте", "👦 Профиль", "📦 Офферы", "📃 Мануал", "🛠️ Тех Поддержка"]

button1 = KeyboardButton(text = "📌 О проекте", callback_data="info")
button2 = KeyboardButton(text = "👦 Профиль", callback_data="profile")
button3 = KeyboardButton(text = "📦 Офферы", callback_data="offers")
button4 = KeyboardButton(text = "📃 Мануал", url="")
button5 = KeyboardButton(text = "🛠️ Тех Поддержка", callback_data="tex")


main_keyboard = ReplyKeyboardMarkup(keyboard = [[button1], [button2, button3], [button4, button5]], resize_keyboard=True)

but1 = InlineKeyboardButton(text = "📃️ Мануалы по трафику", url = manual_url)
but2 = InlineKeyboardButton(text = "💼 Навигация по меню", url = navigation_url)

project_keyboard = InlineKeyboardMarkup(inline_keyboard = [[but1], [but2]])
dp_main = Router()

but1 = InlineKeyboardButton(text = "🛠️ Тех Поддержка", url = 't.me/@HighlyHelp_bot')
but2 = InlineKeyboardButton(text = "💼 Мануалы", url = "t.me/Highly_Materials")
manual_keyboard = InlineKeyboardMarkup(inline_keyboard = [[but2]])
tex_keyboard = InlineKeyboardMarkup(inline_keyboard = [[but1]])


@dp_main.message(F.text == "📌 О проекте")
async def about_project(message: types.Message):
    await message.answer(text = info_text, reply_markup = project_keyboard)

@dp_main.message(F.text == "📃 Мануал")
async def about_project(message: types.Message):
    await message.answer(text = "Для ознакомления нажмите на кнопку", reply_markup = manual_keyboard)

@dp_main.message(F.text == "🛠️ Тех Поддержка")
async def about_project(message: types.Message):
    await message.answer(text = "Для перехода в тех поддержку нажмите на кнопку", reply_markup = tex_keyboard)


@dp_main.message(F.text == "/start")
async def handler(message: types.Message):
    logger.info(f'Сообщение: {message.text} от {message.from_user.id}')
    text = f"""👋 Привет, {message.from_user.first_name}\n\nДобро пожаловать в бота <b>Highly Agency</b> - твой инструмент для управления трафиком.
📌 Используйте меню ниже для удобной навигации и начала работы.
                """
    await message.answer(text=text, parse_mode="HTML", reply_markup = main_keyboard)

@dp_main.callback_query(lambda c: c.data == "menu")
async def menu(callback_query: types.CallbackQuery):
    await handler(callback_query.message)


@dp_main.poll_answer()
async def poll_answer_handler(poll_answer: PollAnswer):
    user_id = poll_answer.user.id
    answer_ids = poll_answer.option_ids

    print(f"Пользователь {user_id} ответил: {answer_ids}")