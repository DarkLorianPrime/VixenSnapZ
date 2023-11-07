from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from routers.authorization.pydantic_models import (
    AuthorizationModel,
    RegistrationReturn,
    AuthorizationReturn,
    GetMe,
    GetUser,
    RegistrationModel
)
from routers.authorization.responses import Responses
from routers.authorization.service import Service, get_user

router = APIRouter()
users_router = APIRouter(prefix="/users")


@router.post(
    "/registration/",
    response_model=RegistrationReturn,
    status_code=201
)
async def create_account(
        credentials: Annotated[RegistrationModel, Depends(RegistrationModel.to_form)],
        service: Annotated[Service, Depends()]
):
    if await service.is_user_exists(credentials.username, credentials.email):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.ACCOUNT_EXISTS)

    return await service.create_user(credentials)


@router.post(
    "/token/",
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
