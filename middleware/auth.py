from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import Message, FSInputFile, ChatMember
from aiogram import Bot, BaseMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Awaitable, Dict, Any, Callable
from time import time as t
import random, os, asyncio
from dotenv import load_dotenv

from db.CRUD import get_user_by_id, create_user
from db.create_database import get_session
from logs.loger_cfg import logger

load_dotenv()

answers: list = ['М̶я̶ч̶', 'Р̶а̶д̶у̶г̶у̶', 'П̶а̶н̶д̶у̶', 'Л̶я̶г̶у̶ш̶к̶у̶', 'П̶и̶н̶г̶в̶и̶н̶а̶']

pictures_for_questions: list = ["⚽️", "🌈", "🐼", "🐸", "🐧"]

USER_CAPTCHA: dict = {}

LIST_TO_SUB: list = ['-1002168727254', '-1002176918802']


button1 = InlineKeyboardButton(text="Чат Highly Agency", url="t.me/Highly_Agency")
button2 = InlineKeyboardButton(text="Основной канал Highly Agency", url="t.me/Highly_Chat")
button3 = InlineKeyboardButton(text="✅ Подписался", callback_data = "menu")
keyboard = InlineKeyboardMarkup(inline_keyboard = [[button1], [button2], [button3]])



class PrivateMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, session_maker):
        super().__init__()
        self.bot = bot
        self.session_maker = session_maker
        self.time = os.getenv("TIME")

    async def __call__(
           self,
                handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                event: Message,
                data: Dict[str, Any]
    ) -> Any:
        if event.chat.type == "private":
            logger.info("Пользователь в приватном чате")
            return await handler(event, data)
        else:
            logger.info("Пользователь не в приват чате")
            return



class CaptchaMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, session_maker):
        super().__init__()
        self.bot = bot
        self.session_maker = session_maker
        self.time = os.getenv("TIME")


    async def check_subscription(self, user_id: int | str, channel_id: int | str) -> bool:
        try:
            member = await self.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            print(member)
            return member.status != "left"

        except Exception as e:
            print(f'[ERROR] Sub {e}')
            return False

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        print("in middleware")
        async with self.session_maker() as session:
            user_in_db = await get_user_by_id(session, event.from_user.id)

            if user_in_db is not None:

                list_not_sub: list = []
                for channel in LIST_TO_SUB:
                    if not await self.check_subscription(event.from_user.id, channel):
                        list_not_sub.append(channel)

                if len(list_not_sub) > 0:
                    text = "Для начала работы с ботом нужно подписаться на наши каналы:"
                    await self.bot.send_message(event.from_user.id, text, reply_markup=keyboard)
                    return

                else:
                    logger.info(F'Пользователь {event.from_user.id} подписан на все каналы')
                    return await handler(event, data)

            user_captcha = USER_CAPTCHA.get(str(event.from_user.id))
            if user_captcha:
                if str(user_captcha["answer"]) == str(event.text):
                    # Создаем пользователя через ту же сессию
                    await create_user(
                        session = session,
                        user_id = event.from_user.id,
                        username = event.from_user.username,
                        captcha = True,
                        is_admin = False
                    )
                    logger.info(f'Создан новый пользователь - {event.from_user.username}')
                    del USER_CAPTCHA[str(event.from_user.id)]
                    await event.answer("✅ Капча пройдена! Добро пожаловать.")
                    return await handler(event, data)
                else:
                    await self.bot.delete_message(message_id=event.message_id, chat_id=event.chat.id)
                    return

            else:
                user_num = random.randint(0, 4)
                await self.bot.send_poll(
                    chat_id = event.chat.id,
                    question = f"Для продолжения выберите {answers[user_num]}",
                    options = pictures_for_questions,
                    is_anonymous = False,
                    type = "quiz",
                    correct_option_id = user_num
                )
                USER_CAPTCHA[str(event.from_user.id)] = {
                    "answer": user_num
                }



class AnswerMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, session_maker):
        super().__init__()
        self.bot = bot
        self.session_maker = session_maker
        self.time = os.getenv("TIME")

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        logger.info("In Answer Middleware")
        async with self.session_maker() as session:
            user_captcha = USER_CAPTCHA.get(str(event.user.id))
            if user_captcha:
                print(str(user_captcha["answer"]), str(event.option_ids))
                if str(user_captcha["answer"]) == str(event.option_ids)[1]:
                    print("USER SAY: ", event.option_ids)
                    await create_user(
                        session=session,
                        user_id=event.user.id,
                        username=event.user.username,
                        captcha=True,
                        is_admin=False
                    )
                    logger.info(f'Создан новый пользователь - {event.user.username}')
                    del USER_CAPTCHA[str(event.user.id)]
                    await self.bot.send_message(event.user.id, text = "✅ Капча пройдена! Добро пожаловать.")
                    return await handler(event, data)
                else:
                    await self.bot.send_message(event.user.id, text = f"Капча не пройденa\n"
                                                f"Вы заблокированы на 30 сек",
                                                )

                    await asyncio.sleep(29)
                    del USER_CAPTCHA[str(event.user.id)]
                    return
