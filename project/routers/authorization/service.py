import hashlib
import os
import uuid

from fastapi import Depends, HTTPException
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from libraries.database import get_session
from libraries.decorators import logger
from routers.authorization.models import User, UserLogs
from routers.authorization.responses import Responses


class PasswordMethods:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.token = os.getenv("ACCESS_KEY").encode()

    async def create_password(self, password: str) -> hex:
        """
        :param password: пароль для шифровки
        :return: зашифрованный пароль
        """
        return hashlib.sha256(self.token + password.encode()).hexdigest()

    async def check_password(self, password: str, username: str):
        """
        :param password: пароль для сравнения (хэшируется и сравнивается с базой данных)
        :param username: логин для сравнения (кому принадлежит пароль)
        :return: Model instance
        """
        password = await self.create_password(password)
        query = await self.session.execute(select(User).where(User.username == username, User.password == password))
        return query.scalars().first()


class Service:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.password_manager = PasswordMethods(session)

    @logger("create user")
    async def create_user(self, credentials: dict):
        is_exists = await self.session.execute(exists().where(User.username == credentials["username"]).select())

        if is_exists.scalar():
            raise HTTPException(status_code=400, detail=Responses.ACCOUNT_EXISTS)

        credentials["password"] = await self.password_manager.create_password(credentials["password"])

        user = User(**credentials)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user.__dict__

    @logger("auth user")
    async def get_user_token(self, credentials: dict) -> uuid.UUID:
        user = await self.password_manager.check_password(**credentials)
        if user is None:
            raise HTTPException(status_code=403, detail=Responses.LOGIN_OR_PASSWORD_NF)

        return user.__dict__

    async def get_user_by_token(self, token: str | uuid.UUID):
        query = await self.session.execute(select(User).where(User.access_token == token))
        return query.scalars().first()

    async def insert_into_logger(self, user_id: uuid.UUID, event: str):
        user_logs = UserLogs(user_id=user_id, event=event)
        self.session.add(user_logs)
        await self.session.commit()
