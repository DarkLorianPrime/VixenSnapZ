import datetime
import uuid

from sqlalchemy import String, DateTime, func, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from storages.database import Base


class User(Base):
    __tablename__ = "user"

    # global
    username: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    avatar: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    registration_date: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    access_token: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)

    # oauth
    user_id: Mapped[int] = mapped_column(Integer, nullable=True)

    # backend
    password: Mapped[str] = mapped_column(String, nullable=True)


class Notify(Base):
    __tablename__ = "notify"

    type: Mapped[str] = mapped_column(String)  # Тип уведомления
    message: Mapped[str] = mapped_column(String)  # Текст
    is_readed: Mapped[bool] = mapped_column(Boolean)  # Было ли прочитано
    alert: Mapped[bool] = mapped_column(Boolean)  # Срочное ли


class Favourites(Base):
    __tablename__ = "favourites"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"))
    frame_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("frame.id"))


class SubscribeUsers(Base):
    __tablename__ = "subscribe_users"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"))
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"))
