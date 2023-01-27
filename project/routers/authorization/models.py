import uuid

from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from libraries.database import base


class User(base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), nullable=False, unique=True, primary_key=True, default=uuid.uuid4)
    password = Column(String)
    access_token = Column(UUID(as_uuid=True), default=uuid.uuid4)
    username = Column(String)
    registration_date = Column(DateTime, server_default=func.now())


class UserLogs(base):
    __tablename__ = "userlogs"
    id = Column(UUID(as_uuid=True), nullable=False, unique=True, primary_key=True, default=uuid.uuid4)
    event = Column(String)
    timestamp = Column(DateTime, server_default=func.now())
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
