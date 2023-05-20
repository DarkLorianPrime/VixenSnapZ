from json import JSONDecodeError
from typing import Self

from pydantic import BaseModel
from starlette.requests import Request


class CustomModel(BaseModel):
    @classmethod
    async def to_form(cls, request: Request) -> Self:
        data = await request.form()
        if not data:
            try:
                data = await request.json()
            except JSONDecodeError:
                data = {}

        return cls(**data)
