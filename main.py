from pickle import GLOBAL

from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
import os, asyncio, aiohttp

from sqlalchemy import lambda_stmt

from middleware.auth import CaptchaMiddleware, AnswerMiddleware, PrivateMiddleware
from db.create_database import get_session, init_db
from logs.loger_cfg import logger
from profile.profile_router import pro_router
from main_menu.main_router import dp_main
from profile.profile_router import usd_to_rub, top_users
from money_out_.money_out import out


load_dotenv()

TOKEN = os.getenv("TOKEN")



async def main():

    await init_db()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.message.middleware(CaptchaMiddleware(bot, get_session()))
    dp.message.middleware(PrivateMiddleware(bot, get_session()))
    dp.poll_answer.middleware(AnswerMiddleware(bot, get_session()))
    # dp.callback_query.middleware(PrivateMiddleware(bot, get_session()))


    dp.include_router(pro_router)
    dp.include_router(out)

    dp.include_router(dp_main)



    await dp.start_polling(bot)



async def tasks():
    task_usd: asyncio.Task = asyncio.create_task(usd_to_rub())
    task_main: asyncio.Task = asyncio.create_task(main())
    task_top: asyncio.Task = asyncio.create_task(top_users())
    await asyncio.gather(task_usd, task_main, top_users())



if __name__ == '__main__':
    asyncio.run(tasks())
