import re

from fastapi import HTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from routers.authorization.responses import Responses


def username_validate(value: str) -> str:
    if not re.fullmatch(r"^[A-Za-z0-9]+(?:[ _-][A-Za-z0-9]+)*$", value):
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=Responses.USERNAME_NOT_VALID)

    return value


def password_validate(password: str) -> str:
    if not re.fullmatch(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password):
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=Responses.NOT_VALID_CYRILLIC_OR_LENGTH)

    return password


def email_validate(value: str) -> str:
    if not re.fullmatch(r"^\S+@\S+\.\S+$", value):
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=Responses.EMAIL_NOT_VALID)

    return value
