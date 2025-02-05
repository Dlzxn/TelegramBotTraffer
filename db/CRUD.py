from datetime import datetime

from sqlalchemy.future import select
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.create_tables import Ticket
from logs.loger_cfg import logger
from sqlalchemy.orm import selectinload
from sqlalchemy import update, delete, and_

from db.create_tables import User, Offer
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


from sqlalchemy import update


async def update_user_privacy(session: AsyncSession, user_id: int | str, is_private:bool):
    try:
        new_status = not is_private
        async with session.begin():
            stmt = (
                update(User)
                .where(User.telegram_id == user_id)
                .values(is_private=new_status)
                .execution_options(synchronize_session="fetch")
            )
            result = await session.execute(stmt)

            if result.rowcount == 0:
                logger.warning(f"Пользователь с ID {user_id} не найден")
                return False

            logger.info(f"Статус обновлен для пользователя {user_id}")
            return True
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await session.rollback()
        return False

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
    async with session_maker as session:
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



async def get_user_info_by_username(session_maker, username: str):
    """Получить всю информацию о пользователе по его Telegram ID"""
    async with session_maker as session:
        stmt = select(User).where(User.username == username)
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
            logger.info(f"Пользователь с ID {username} не найден")
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




# Создание оффера
async def create_offer(
    session: AsyncSession,
    name: str,
    money: int,
    action: str,
    geo: str,
    commentary: str | None = None,
    user_id: int | None = None,
    url: str | None = None
):
    """Создание нового оффера"""
    async with session.begin():
        new_offer = Offer(
            name=name,
            money=money,
            action=action,
            geo=geo,
            commentary=commentary,
            user_id=user_id,
            url=url,
        )
        session.add(new_offer)
        await session.commit()
    return new_offer


# Поиск всех офферов по user_id
async def get_offers_by_user_id_two(session: AsyncSession, user_id: str | int):
    """Получение всех офферов для указанного user_id"""
    async with session.begin():
        query = await session.execute(
            select(Offer).where(Offer.user_id == user_id).options(selectinload("*"))
        )
        return query.scalars().all()

async def get_offer_by_id(session: AsyncSession, id: int):
    """Получение всех офферов для указанного user_id"""
    async with session.begin():
        query = await session.execute(
            select(Offer).where(Offer.id == id).options(selectinload("*"))
        )
        return query.scalars().all()


async def get_all_offers(session: AsyncSession):
    """Получение всех офферов для указанного user_id"""
    async with session.begin():
        query = select(Offer).where(
            and_(Offer.url == None, Offer.user_id.isnot(""))
        ).options(selectinload("*"))
        return query.scalars().all()

# Удаление оффера
async def delete_offer(session: AsyncSession, offer_id: int):
    """Удаление оффера по ID"""
    async with session.begin():
        query = delete(Offer).where(Offer.id == offer_id)
        result = await session.execute(query)
        await session.commit()
        return result.rowcount > 0  # True, если что-то удалено


# Добавление ссылки по ID оффера
async def add_url_to_offer(session: AsyncSession, offer_id: int, url: str):
    """Добавление ссылки в оффер"""
    async with session.begin():
        query = update(Offer).where(Offer.id == offer_id).values(url=url)
        result = await session.execute(query)
        await session.commit()
        return result.rowcount > 0  # True, если обновлено


async def assign_user_to_offer(session: AsyncSession, offer_id: int, user_id: int):
    """Привязка пользователя к офферу"""
    try:
        # Получаем оффер по ID
        offer = await session.get(Offer, offer_id)
        if not offer:
            logger.info(f"Оффер с ID {offer_id} не найден.")
            return False

        # Обновляем пользователя для найденного оффера
        logger.info(f"USER ID IN OFFER {user_id}")
        offer.user_id += f" {user_id}"
        await session.commit()

        logger.info(f"Пользователь с ID {user_id} привязан к офферу с ID {offer_id}.")
        return True
    except Exception as e:
        logger.error(f"Ошибка при привязке пользователя к офферу: {e}")
        return False


async def update_offer_action(session: AsyncSession, offer_id: int, new_action: str):
    # Найдем оффер по id
    query = select(Offer).where(Offer.id == offer_id)
    result = await session.execute(query)
    offer = result.scalar_one_or_none()

    # Если оффер найден, обновляем action
    if offer:
        offer.action = new_action
        await session.commit()
        return offer
    return None  # если оффер не найден


async def update_offer_commentary(session: AsyncSession, offer_id: int, new_commentary: str):
    # Найдем оффер по id
    query = select(Offer).where(Offer.id == offer_id)
    result = await session.execute(query)
    offer = result.scalar_one_or_none()

    # Если оффер найден, обновляем commentary
    if offer:
        offer.commentary = new_commentary
        await session.commit()
        return offer
    return None  # если оффер не найден



async def get_all_offers(session: AsyncSession):
    """Получение всех офферов"""
    async with session.begin():
        result = await session.execute(select(Offer))  # Запрос для получения всех офферов
        offers = result.scalars().all()

    return offers



async def update_offer_name(db: AsyncSession, offer_id: int, new_name: str):
    # Получаем оффер по ID
    result = await db.execute(select(Offer).filter(Offer.id == offer_id))
    offer = result.scalars().first()
    if offer:
        # Обновляем имя оффера
        offer.button_name = new_name
        # Коммитим изменения в базе данных
        await db.commit()
        await db.refresh(offer)  # Обновляем объект после коммита
        logger.info(f"Rename {offer_id}: {new_name}")
        return offer
    else:
        return None  # Возвращаем None, если оффер не найден


async def get_offers_by_user_id(session: AsyncSession, user_id: int):
    """Получение всех офферов"""
    async with session.begin():
        result = await session.execute(select(Offer))  # Запрос для получения всех офферов
        offers = result.scalars().all()
    offers_return: list = []
    for offer in offers:
        logger.info(f"Оффер принадлежит: {offer.user_id}")
        if str(user_id) in offer.user_id.split():
            offers_return.append(offer)
    return offers_return


async def get_user_by_username(session: AsyncSession, username: str):
    """Получить пользователя по username"""
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    return result.scalars().first()
