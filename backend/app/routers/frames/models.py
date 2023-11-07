import datetime
import uuid

from sqlalchemy import String, ForeignKey, Boolean, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from storages.database import Base
from storages.types.files import File


class Frame(Base):
    __tablename__ = "frame"

    short_url: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, nullable=True)
    category: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("category.id"))
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_onupdate=func.now(),
                                                          server_default=func.now())


class Attachments(Base):
    __tablename__ = "attached"

    order: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str] = mapped_column(File(is_need_folder=True, bucket="frames"))
    frame_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("frame.id"))


class Commentaries(Base):
    __tablename__ = "commentaries"

    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"))
    frame_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("frame.id"))
    text: Mapped[str] = mapped_column(String)


class Likes(Base):
    __tablename__ = "likes"

    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"))
    frame_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("frame.id"), nullable=True)
    commentary_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("commentaries.id"), nullable=True)
    is_positive: Mapped[bool] = mapped_column(Boolean)


class CommentLikes(Base):
    __tablename__ = "comment_likes"


class Views(Base):
    __tablename__ = "views"

    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"))
    frame_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("frame.id"))


class Tags(Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("category.id"))
