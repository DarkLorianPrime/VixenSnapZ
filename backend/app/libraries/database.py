from os import getenv

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

base = declarative_base()
postgres_user = getenv("POSTGRES_USER")
postgres_password = getenv("POSTGRES_PASSWORD")
postgres_host = getenv("POSTGRES_HOST")
postgres_name = getenv("POSTGRES_NAME")

url = f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}/{postgres_name}"
engine = create_async_engine(url)

session = async_sessionmaker(bind=engine, class_=AsyncSession)


async def get_session() -> AsyncSession:
    async with session(expire_on_commit=False) as s:
        yield s
