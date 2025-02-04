from sqlalchemy.future import select

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


async def get_user_info_by_id(session, user_id: int | str):
    """Получить всю информацию о пользователе по его Telegram ID"""
    async with session:
        stmt = select(User).where(User.telegram_id == user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()

        if user:
            logger.info(f"Информация о пользователе {user.username} найдена!")
            return user
        else:
            logger.info(f"Пользователь с ID {user_id} не найден")
            return None

