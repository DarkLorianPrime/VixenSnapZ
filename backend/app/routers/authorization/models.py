import uuid

from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from libraries.database import base


class User(base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), nullable=False, unique=True, primary_key=True, default=uuid.uuid4)
    password = Column(String)
    access_token = Column(UUID(as_uuid=True), default=uuid.uuid4)
    username = Column(String)
    registration_date = Column(DateTime, server_default=func.now())
