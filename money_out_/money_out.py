from aiogram import Router
from aiogram.fsm import state
from aiogram.types import CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile, FSInputFile


from db.CRUD import get_session, get_user_info_by_id, create_ticket, get_tickets_by_user
from logs.loger_cfg import logger


out = Router()

but1 = InlineKeyboardButton(text = "Выйти из формы", callback_data="exit_form")

keyword_out_money = InlineKeyboardMarkup(inline_keyboard=[[but1]])

class OutputForm(StatesGroup):
    Summary = State()
    Bank_name = State()
    Card_number = State()
    Commentary = State()




@out.callback_query(lambda c: c.data == "output_money")
async def out_menu(c: CallbackQuery, state: FSMContext):
    user_tickets = await get_tickets_by_user(get_session(), c.from_user.id)

    logger.info("Выводы пользователя:" ,user_tickets)
    all_status = True
    p = 0
    for i in range(len(user_tickets)):
        if user_tickets[i].status == "🕐 Создана":
            all_status = False
            p = i
            break

    if all_status:
        await c.message.answer("Введите cумму в RUB", reply_markup=keyword_out_money)

        await state.set_state(OutputForm.Summary)


    else:
        await c.message.answer(f"Вы уже подавали заявку на вывод!\n"
                               f"Данные заявки id:"
                               f" {user_tickets[p].id}\n"
                               f" Сумма: {user_tickets[p].money_out}\n"
                               f" Статус: {user_tickets[p].status}\n"
                               )


@out.message(OutputForm.Summary)
async def get_name(message: Message, state: FSMContext):
    try:
        await state.update_data(sum=int(message.text))
        async with get_session()() as session:
            user = await get_user_info_by_id(session, message.from_user.id)
            if user.money >= int(message.text):
                await message.answer("Выберите способ вывода(название банка/номер/крипта)", reply_markup=keyword_out_money)
                await state.set_state(OutputForm.Bank_name)

            else:
                await message.answer("Не хватает средств на счету")

    except Exception as e:
        logger.error(e)
        await message.answer("Должно быть число")

@out.message(OutputForm.Bank_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(bank=message.text)  # Сохраняем имя
    await message.answer("Введите номер карты/телефона/счета", reply_markup=keyword_out_money)
    await state.set_state(OutputForm.Card_number)

@out.message(OutputForm.Card_number)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(card_num=message.text)  # Сохраняем имя
    await message.answer("Введите комментарии к выводу", reply_markup=keyword_out_money)
    await state.set_state(OutputForm.Commentary)


@out.message(OutputForm.Commentary)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)  # Сохраняем имя
    data = await state.get_data()
    print(data)
    ticket = await create_ticket(get_session(), message.from_user.id, data['sum'], data['bank'], data["card_num"], data["comment"])
    await message.reply(f"✅Заявка на вывод id{ticket.id} Успешно создана!\n\n"
                        f"⏳Ваш запрос обрабатывается, средства будут перечислены в течении 24 часов!\n")
    await state.clear()



@out.callback_query(lambda c: c.data == "exit_form")
async def exit_form(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.answer("Вы вышли, для продолжения /start")







