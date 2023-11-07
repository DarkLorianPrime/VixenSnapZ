import hashlib
import os
import uuid
from typing import Annotated, List, Sequence

from fastapi import Depends, HTTPException
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_401_UNAUTHORIZED

from routers import oauth2
from storages.database import get_session
from routers.authorization.models import User
from routers.authorization.pydantic_models import AuthorizationModel, RegistrationModel
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

    async def check_password(self, password: str, username: str = None, email: str = None):
        """
        :param email: почта для сравнения (кому принадлежит пароль)
        :param password: пароль для сравнения (хэшируется и сравнивается с базой данных)
        :param username: логин для сравнения (кому принадлежит пароль)
        :return: Model instance
        """
        password = await self.create_password(password)
        query = [User.password == password]
        if username:
            query.append(User.username == username)

        if email:
            query.append(User.email == email)

        query = await self.session.execute(select(User).where(*query))
        return query.scalars().first()


class Service:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.password_manager = PasswordMethods(session)

    async def is_user_exists(self, username=None, email=None) -> bool:
        query = []
        if username:
            query.append(User.username == username)

        if email:
            query.append(User.email == email)

        stmt = exists().where(*query).select()
        result = await self.session.execute(stmt)
        return result.scalar()

    async def create_user(self, credentials: RegistrationModel) -> User:
        password = await self.password_manager.create_password(credentials.password)
        credentials = credentials.dict()
        credentials["password"] = password

        user = User(**credentials)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_token(self, credentials: AuthorizationModel) -> uuid.UUID:
        if not credentials.username and not credentials.email:
            raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=Responses.NOT_EMAIL_NOT_USERNAME)

        user = await self.password_manager.check_password(
            username=credentials.username,
            email=credentials.email,
            password=credentials.password
        )

        if user is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=Responses.LOGIN_OR_PASSWORD_NF)

        return user.access_token

    async def get_user_by_token(self, token: str | uuid.UUID) -> User:
        stmt = select(User).where(User.access_token == token)
        query = await self.session.execute(stmt)
        return query.scalars().first()

    async def get_users(self) -> Sequence[User]:
        stmt = select(User)
        query = await self.session.execute(stmt)
        return query.scalars().all()


async def get_user(
        token: Annotated[str, Depends(oauth2)],
        service: Annotated[Service, Depends()]
) -> User | None:
    user = await service.get_user_by_token(token)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
