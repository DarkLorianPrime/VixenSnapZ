from fastapi import APIRouter, Depends, Security, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from libraries.authenticator import verifier
from routers.authorization.pydantic_models import AuthorizationModel, RegistrationReturn, AuthorizationReturn, GetMe
from routers.authorization.responses import Responses
from routers.authorization.service import Service

router = APIRouter()


@router.post("/registration/", response_model=RegistrationReturn, status_code=201)
async def create_account(credentials: AuthorizationModel = Depends(AuthorizationModel.to_form),
                         service: Service = Depends(Service)):

    if await service.is_user_exists(credentials.username):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.ACCOUNT_EXISTS)

    return await service.create_user(credentials)


@router.post("/login/", response_model=AuthorizationReturn)
async def authorize(credentials: AuthorizationModel = Depends(AuthorizationModel.to_form),
                    service: Service = Depends(Service)):
    return {"access_token": await service.get_user_token(credentials)}


@router.get("/users/me/", response_model=GetMe)
async def get_me(credentials: verifier = Security(verifier)):
    return credentials
