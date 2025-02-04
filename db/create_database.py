from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv
import os, asyncio, logging

load_dotenv()

engine = None
SessionLocal = None


async def init_db():
    """Инициализация БД (должна вызываться в основном event loop)"""
    global engine, SessionLocal

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        if not await conn.run_sync(lambda c: database_exists(engine.url)):
            await conn.run_sync(lambda c: create_database(engine.url))

    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    return engine, SessionLocal


def get_session():
    """Функция для получения sessionmaker (для использования в других модулях)"""
    if not SessionLocal:
        raise RuntimeError("Database not initialized! Call init_db() first")
    return SessionLocal

