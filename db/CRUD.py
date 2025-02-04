from datetime import datetime

from sqlalchemy.future import select
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.create_tables import Ticket
from logs.loger_cfg import logger

from db.create_tables import User
from logs.loger_cfg import logger
from db.create_database import get_session


async def create_user(session, user_id: int | str, username: str | None, captcha: bool, is_admin: bool):
    """Асинхронное создание пользователя в БД"""
    async with session:
        async with session.begin():
            new_user = User(telegram_id=user_id, username=username, captcha=captcha, is_admin=is_admin)
            session.add(new_user)
            await session.commit()  # Асинхронный commit

        logger.info(f"Пользователь {username} добавлен в БД.")

async def get_user_by_id(session, user_id: str | int) -> User | None:
    """Асинхронный поиск пользователя по ID"""
    async with session:
        stmt = select(User).where(User.telegram_id == user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()

        if user:
            logger.info(f'Пользователь {user.username} найден')
            return user

        logger.info(f"Пользователь с ID {user_id} не найден")
        return None


async def get_all_users(session: AsyncSession) -> list:
    """Ассоциированный поиск всех пользователей"""
    stmt = select(User)
    result = await session.execute(stmt)
    users = result.scalars().all()  # Получаем все пользователи
    return users




async def update_is_private(session, user_id: int | str, new_status: bool):
    """Изменить статус is_private пользователя в БД"""
    async with session:
        async with session.begin():
            stmt = select(User).where(User.telegram_id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()

            if user:
                user.is_private = new_status
                await session.commit()  # Асинхронный commit
                logger.info(f"Статус 'is_private' пользователя {user.username} обновлен на {new_status}")
            else:
                logger.info(f"Пользователь с ID {user_id} не найден")




async def add_money(session, user_id: int | str, amount: int):
    """Добавить деньги пользователю в БД"""
    if amount <= 0:
        logger.error("Сумма добавления денег должна быть положительной.")
        return

    async with session:
        async with session.begin():
            stmt = select(User).where(User.telegram_id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()

            if user:
                user.money += amount
                await session.commit()  # Асинхронный commit
                logger.info(f"Пользователю {user.username} добавлено {amount} денег.")
            else:
                logger.info(f"Пользователь с ID {user_id} не найден")


async def deduct_money(session, user_id: int | str, amount: int):
    """Списать деньги с пользователя в БД"""
    if amount <= 0:
        logger.error("Сумма списания денег должна быть положительной.")
        return

    async with session:
        async with session.begin():
            stmt = select(User).where(User.telegram_id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()

            if user:
                if user.money >= amount:
                    user.money -= amount
                    await session.commit()  # Асинхронный commit
                    logger.info(f"С пользователя {user.username} списано {amount} денег.")
                else:
                    logger.error(f"У пользователя {user.username} недостаточно средств.")
            else:
                logger.info(f"Пользователь с ID {user_id} не найден")


async def add_lids(session, user_id: int | str, amount: int):
    """Добавить количество lids пользователю в БД"""
    if amount <= 0:
        logger.error("Сумма добавления lids должна быть положительной.")
        return

    async with session:
        async with session.begin():
            stmt = select(User).where(User.telegram_id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()

            if user:
                user.lids += amount
                await session.commit()  # Асинхронный commit
                logger.info(f"Пользователю {user.username} добавлено {amount} lids.")
            else:
                logger.info(f"Пользователь с ID {user_id} не найден")



async def remove_lids(session, user_id: int | str, amount: int):
    """Удалить количество lids у пользователя в БД"""
    if amount <= 0:
        logger.error("Сумма удаления lids должна быть положительной.")
        return

    async with session:
        async with session.begin():
            stmt = select(User).where(User.telegram_id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()

            if user:
                if user.lids >= amount:
                    user.lids -= amount
                    await session.commit()  # Асинхронный commit
                    logger.info(f"У пользователя {user.username} удалено {amount} lids.")
                else:
                    logger.error(f"У пользователя {user.username} недостаточно lids.")
            else:
                logger.info(f"Пользователь с ID {user_id} не найден")


async def get_user_info_by_id(session_maker, user_id: int | str):
    """Получить всю информацию о пользователе по его Telegram ID"""
    async with session_maker() as session:
        stmt = select(User).where(User.telegram_id == user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()

        if user:
            logger.info(f"Информация о пользователе {user.username}:")
            logger.info(f"ID: {user.id}")
            logger.info(f"Telegram ID: {user.telegram_id}")
            logger.info(f"Username: {user.username}")
            logger.info(f"Captcha: {user.captcha}")
            logger.info(f"Is Admin: {user.is_admin}")
            logger.info(f"Is Private: {user.is_private}")
            logger.info(f"Money: {user.money}")
            logger.info(f"Lids: {user.lids}")
            return user
        else:
            logger.info(f"Пользователь с ID {user_id} не найден")
            return None


async def create_ticket(session_maker, user_id: int, money_out: int, bank: str, card_number: str,
                        commentary: str | None):
    """Создать новый тикет на вывод средств"""
    async with session_maker() as session:  # Создаем сессию
        async with session.begin():  # Начинаем транзакцию
            ticket = Ticket(
                id_user=user_id,
                money_out=money_out,
                bank=bank,
                card_number=card_number,
                commentary=commentary,
                time_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            session.add(ticket)  # Добавляем в сессию
            await session.commit()  # Фиксируем изменения

        return ticket  # Возвращаем созданный тикет


async def get_ticket_by_id(session: AsyncSession, ticket_id: int):
    """Получение тикета по ID"""
    async with session.begin():
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        result = await session.execute(stmt)
        ticket = result.scalars().first()
        return ticket

async def get_tickets_by_user(session_maker, user_id: int):
    """Получить все тикеты пользователя по его Telegram ID"""
    async with session_maker() as session:  # Создаем сессию
        stmt = select(Ticket).where(Ticket.id_user == user_id)
        result = await session.execute(stmt)
        return result.scalars().all()  # Возвращаем все тикеты пользователя


async def update_ticket_status(session: AsyncSession, ticket_id: int, new_status: str):
    """Обновление статуса тикета"""
    async with session.begin():
        ticket = await get_ticket_by_id(session, ticket_id)
        if ticket:
            ticket.status = new_status
            await session.commit()
            logger.info(f"Обновлен статус тикета #{ticket_id} на {new_status}")
            return ticket
        return None

async def delete_ticket(session: AsyncSession, ticket_id: int):
    """Удаление тикета по ID"""
    async with session.begin():
        ticket = await get_ticket_by_id(session, ticket_id)
        if ticket:
            await session.delete(ticket)
            await session.commit()
            logger.info(f"Удален тикет #{ticket_id}")
            return True
        return False


