from os import getenv

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

base = declarative_base()

engine = create_async_engine(f"postgresql+asyncpg://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@{getenv('DB_HOST')}/{getenv('DB_NAME')}")
session = sessionmaker(bind=engine, class_=AsyncSession)


async def get_session() -> AsyncSession:
    async with session(expire_on_commit=False) as s:
        yield s
