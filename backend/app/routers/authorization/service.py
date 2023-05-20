import hashlib
import os
import uuid

from fastapi import Depends, HTTPException
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from libraries.database import get_session
from routers.authorization.models import User
from routers.authorization.pydantic_models import AuthorizationModel
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

    async def is_user_exists(self, username) -> bool:
        stmt = exists().where(User.username == username).select()
        result = await self.session.execute(stmt)
        return result.scalar()

    async def create_user(self, credentials: AuthorizationModel) -> User:
        password = await self.password_manager.create_password(credentials.password)
        credentials = credentials.dict()
        credentials["password"] = password

        user = User(**credentials)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_token(self, credentials: AuthorizationModel) -> uuid.UUID:
        user = await self.password_manager.check_password(username=credentials.username, password=credentials.password)

        if user is None:
            raise HTTPException(status_code=404, detail=Responses.LOGIN_OR_PASSWORD_NF)

        return user.access_token

    async def get_user_by_token(self, token: str | uuid.UUID) -> User:
        query = await self.session.execute(select(User).where(User.access_token == token))
        return query.scalars().first()
