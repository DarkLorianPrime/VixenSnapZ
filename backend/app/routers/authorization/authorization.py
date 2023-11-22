import uuid
from typing import Annotated, List

import httpx
from fastapi import APIRouter, Depends, HTTPException
from httpx import AsyncClient
from starlette.status import HTTP_400_BAD_REQUEST

from routers.authorization.pydantic_models import (
    AuthorizationModel,
    RegistrationReturn,
    AuthorizationReturn,
    GetMe,
    GetUser,
    RegistrationRequestModel, OAuthModel
)
from routers.authorization.responses import Responses
from routers.authorization.service import Service, get_user

router = APIRouter(prefix="/token")
users_router = APIRouter(prefix="/users")


@router.post("/oauth/")
async def oauth_login(
        credentials: Annotated[OAuthModel, Depends(OAuthModel.to_form)],
        service: Annotated[Service, Depends()]
):
    async with AsyncClient() as client:
        result = await client.get(
            "https://api.vk.com/method/users.get",
            headers={"Authorization": f"Bearer {credentials.access_token}"},
            params={"fields": "screen_name"}
        )

    result = result.json()["response"][0]
    if result["user_id"] != credentials.user_id:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="sent user_id and user_id from token is not equal")

    user = await service.get_user(oauth_id=credentials.user_id)
    if not user:
        return {"access_token": user.access_token}

    # ДОБАВИТЬ ОБНОВЛЕНИЕ ДАННЫХ ПРИ АУФЕ
    return await service.create_oauth_user(
        {
            "username": user["screen_name"],
            "user_id": credentials.user_id,
            "email": credentials.email,
            "name": f'{user["first_name"]} {user["last_name"]}'
        }
    )


@router.post(
    "/create/",
    response_model=RegistrationReturn,
    status_code=201
)
async def create_account(
        credentials: Annotated[RegistrationRequestModel, Depends(RegistrationRequestModel.to_form)],
        service: Annotated[Service, Depends()]
):
    if await service.is_user_exists(credentials.username, credentials.email):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.ACCOUNT_EXISTS)

    return await service.create_user(credentials)


@router.post(
    "/",
    response_model=AuthorizationReturn
)
async def authorize(
        credentials: Annotated[AuthorizationModel, Depends(AuthorizationModel.to_form)],
        service: Annotated[Service, Depends()]
):
    return {
        "access_token": await service.get_user_token(credentials),
        "type": "bearer"
    }


@users_router.get(
    "/me/",
    response_model=GetMe
)
async def get_users_me(
        user: Annotated[GetMe, Depends(get_user)]
):
    return user


@users_router.get(
    "/",
    response_model=List[GetUser],
    dependencies=[Depends(get_user)]
)
async def get_users(
        service: Annotated[Service, Depends()]
):
    return await service.get_users()


@users_router.get(
    "/{user_id}/",
    response_model=GetUser,
    dependencies=[Depends(get_user)]
)
async def get_user(
        user_id: uuid.UUID,
        service: Annotated[Service, Depends()]
):
    return await service.get_user(user_id)
