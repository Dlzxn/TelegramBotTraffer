from sqlalchemy import Column, BigInteger, String, create_engine, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
import asyncio

from db.create_database import init_db, engine




Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    captcha = Column(Boolean, nullable=False, default=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    is_private = Column(Boolean, nullable=False, default=False)
    money = Column(BigInteger, nullable=False, default=0)
    lids = Column(BigInteger, nullable=False, default=0)
    pay_out = Column(BigInteger, nullable=False, default=0)


class Ticket(Base):
    __tablename__ = "money_out"
    id = Column(BigInteger, primary_key=True, index=True)
    id_user = Column(BigInteger)
    money_out = Column(BigInteger, nullable=False, default=0)
    bank = Column(String, nullable=False)
    card_number = Column(String, nullable=False)
    commentary = Column(String, nullable=True)
    time_created = Column(String, nullable=False, default=0)
    status = Column(String, nullable=False, default="🕐 Создана")



async def create_tables():
    engine, _ = await init_db()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def recreate_tables():
    # Удалить старые таблицы
    engine, _ = await init_db()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Удаление всех таблиц
        await conn.run_sync(Base.metadata.create_all)  # Создание новых таблиц



#
# # Вызов функции для перегенерации таблиц
# asyncio.run(recreate_tables())