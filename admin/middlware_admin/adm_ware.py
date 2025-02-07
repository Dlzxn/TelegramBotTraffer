from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import Message, FSInputFile, ChatMember
from aiogram import Bot, BaseMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Awaitable, Dict, Any, Callable
from time import time as t
import random, os, asyncio

from logs.loger_cfg import logger
from db.CRUD import get_user_info_by_id, get_session



class AdminMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.time = os.getenv("TIME")

    async def __call__(
           self,
                handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                event: Message,
                data: Dict[str, Any]
    ) -> Any:
        logger.info(f"Пользователь в миддлвари {event.from_user.id}")
        async with get_session()() as session:
            user = await get_user_info_by_id(session, event.from_user.id)
            print("USER: ", user)
            if user:
                logger.info(f"Пользователь {user.username} статус админки: {user.is_admin}")
                if user.is_admin:
                    return await handler(event, data)