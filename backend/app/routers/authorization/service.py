import hashlib
import os
import uuid
from typing import Annotated, Sequence

from fastapi import Depends, HTTPException
from sqlalchemy import select, exists, insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from routers import oauth2
from routers.authorization.config import hash_token
from routers.authorization.dependencies import validate_fields_not_empty
from storages.database import get_session
from routers.authorization.models import User
from routers.authorization.pydantic_models import AuthorizationModel, RegistrationModel
from routers.authorization.responses import Responses


class UserRepository:
    def __init__(
            self,
            session: AsyncSession = Depends(get_session),
    ):
        self.session = session

    async def create(self, credentials):
        hashed_password = await self.PasswordMethods.create_password(credentials["password"])
        credentials["password"] = hashed_password
        del credentials["id"]

        stmt = insert(User).values(**credentials).returning(User.id)
        result = await self.session.execute(stmt)

        result_scalar = result.scalars()
        credentials["id"] = result_scalar.first()

        await self.session.commit()
        return credentials

    async def get(
            self,
            username: str = None,
            hashed_password: str = None,
            email: str = None,
            access_token: uuid.UUID = None,
            one: bool = True
    ):
        stmt = select(User)
        query = []

        try:
            uuid.UUID(access_token)
        except ValueError:
            raise HTTPException(HTTP_403_FORBIDDEN, detail="not valid token")
        except TypeError:
            ...

        if username:
            query.append(User.username == username)

        if hashed_password:
            query.append(User.password == hashed_password)

        if email:
            query.append(User.email == email)

        if access_token:
            query.append(User.access_token == access_token)

        stmt = stmt.filter(*query)
        result = await self.session.execute(stmt)
        scalar_result = result.scalars()
        if one:
            return scalar_result.first()

        return scalar_result.all()

    async def authorize(self, password, username: str = None, email: str = None):
        hashed_password = await self.PasswordMethods.create_password(password)
        user = await self.get(
            username=username,
            hashed_password=hashed_password,
            email=email
        )
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=Responses.LOGIN_OR_PASSWORD_NF)

        return user.access_token

    class PasswordMethods:
        @staticmethod
        async def create_password(password: str) -> hex:
            """
            :param password: пароль для шифровки
            :return: зашифрованный пароль
            """
            return hashlib.sha256(hash_token + password.encode()).hexdigest()


class Service:
    def __init__(
            self,
            session: Annotated[AsyncSession, Depends(get_session)],
            users: Annotated[UserRepository, Depends()]
    ):
        self.session = session
        self.users = users

    async def is_user_exists(self, username: str, email: str) -> bool:
        stmt = exists().where(
            User.username == username,
            User.email == email
        ).select()
        result = await self.session.execute(stmt)
        return result.scalar()

    async def create_user(self, credentials: RegistrationModel) -> User:
        credentials = credentials.dict()
        return await self.users.create(credentials)

    async def get_user_token(
            self,
            credentials: Annotated[AuthorizationModel, Depends(validate_fields_not_empty)]
    ) -> uuid.UUID:
        token = await self.users.authorize(
            username=credentials.username,
            email=credentials.email,
            password=credentials.password
        )

        return token

    async def get_user_by_token(self, token: uuid.UUID) -> User:
        user = await self.users.get(access_token=token)
        return user

    async def get_users(self) -> Sequence[User]:
        result = await self.users.get(one=False)
        return result


async def get_user(
        token: Annotated[uuid.UUID, Depends(oauth2)],
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
