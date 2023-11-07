import uuid
from os import getenv

from sqlalchemy import URL, UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
        primary_key=True,
        default=uuid.uuid4
    )

    @property
    def fields(self):
        return self.__dict__


url = URL(
    drivername="postgresql+asyncpg",
    username=getenv("POSTGRES_USER"),
    password=getenv("POSTGRES_PASSWORD"),
    host=getenv("POSTGRES_HOST"),
    database=getenv("POSTGRES_NAME"),
    port=5432,
    query={}
)

engine = create_async_engine(url)

session = async_sessionmaker(bind=engine, class_=AsyncSession)


async def get_session() -> AsyncSession:
    async with session(expire_on_commit=False) as s:
        yield s
