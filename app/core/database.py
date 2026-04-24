from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs,AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

# Асинхронный движок для работы с БД
engine = create_async_engine(
    url=settings.database_url,
    echo=True,
    poolclass=NullPool
)

class Base(AsyncAttrs, DeclarativeBase):
    pass

# Фабрика сессий для взаимодействия с БД
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    """Получить сессию БД"""
    async with async_session_maker() as session:
        yield session