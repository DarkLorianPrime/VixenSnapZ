import datetime
import uuid

from pydantic import BaseModel, validator

from dependencies.pydantic_model import CustomModel
from routers.authorization.validators import password_validate, username_validate, email_validate


class AuthorizationModel(CustomModel):
    username: str | None
    password: str
    email: str | None

    @classmethod
    @validator("email")
    def email_validator(cls, value: str) -> str:
        return email_validate(value)

    @classmethod
    @validator("username")
    def username_validator(cls, value: str) -> str:
        return username_validate(value)

    @classmethod
    @validator("password")
    def password_validator(cls, value: str) -> str:
        return password_validate(value)


class RegistrationModel(CustomModel):
    id: uuid.UUID = None
    username: str
    password: str
    email: str
    name: str

    @classmethod
    @validator("email")
    def email_validator(cls, value: str) -> str:
        return email_validate(value)

    @classmethod
    @validator("username")
    def username_validator(cls, value: str) -> str:
        return username_validate(value)

    @classmethod
    @validator("password")
    def password_validator(cls, value: str) -> str:
        return password_validate(value)


class RegistrationReturn(BaseModel):
    id: uuid.UUID
    username: str
    name: str

    class Config:
        orm_mode = True


class AuthorizationReturn(BaseModel):
    access_token: uuid.UUID
    type: str


class GetUser(BaseModel):
    id: uuid.UUID
    username: str
    name: str
    registration_date: datetime.datetime
    avatar: uuid.UUID | None

    class Config:
        orm_mode = True


class GetMe(GetUser):
    email: str | None


