from fastapi import APIRouter, Depends, Security

from libraries.authenticator import verifier
from routers.authorization.pydantic_models import AuthorizationModel, RegistrationReturn, AuthorizationReturn, GetMe
from routers.authorization.service import Service

router = APIRouter()


@router.post("/registration/", response_model=RegistrationReturn)
async def create_account(credentials: dict = Depends(AuthorizationModel.as_form), service: Service = Depends(Service)):
    return await service.create_user(credentials)


@router.post("/login/", response_model=AuthorizationReturn)
async def authorize(credentials: dict = Depends(AuthorizationModel.as_form), service: Service = Depends(Service)):
    return await service.get_user_token(credentials)


@router.get("/users/me/", response_model=GetMe)
async def get_me(credentials: verifier = Security(verifier)):
    return credentials.__dict__
