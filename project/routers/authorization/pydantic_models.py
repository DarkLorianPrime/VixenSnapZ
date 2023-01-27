import uuid

from pydantic import BaseModel, validator

from libraries.depends import as_form
from routers.authorization.validators import password_validate, username_validate


@as_form
class AuthorizationModel(BaseModel):
    username: str
    password: str

    @validator("username")
    def username_validator(cls, value: str) -> str:
        return username_validate(value)

    @validator("password")
    def password_validator(cls, value: str) -> str:
        return password_validate(value)


class RegistrationReturn(BaseModel):
    id: uuid.UUID
    username: str


class AuthorizationReturn(BaseModel):
    access_token: uuid.UUID


class GetMe(BaseModel):
    id: uuid.UUID
    username: str