import uuid

from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from libraries.database import base


class InBox(base):
    __tablename__ = "inbox"
    id = Column(UUID(as_uuid=True), nullable=False, unique=True, primary_key=True, default=uuid.uuid4)
    filename = Column(String)
    file_uuid = Column(UUID(as_uuid=True))
    bucketname = Column(String)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))


class FramesLogs(base):
    __tablename__ = "frameslogs"
    id = Column(UUID(as_uuid=True), nullable=False, unique=True, primary_key=True, default=uuid.uuid4)
    event = Column(String)
    timestamp = Column(DateTime, server_default=func.now())
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))