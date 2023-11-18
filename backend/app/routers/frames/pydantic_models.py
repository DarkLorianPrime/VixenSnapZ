import uuid
from typing import List, Generic, TypeVar

from pydantic import BaseModel, conint
from pydantic.generics import GenericModel

from dependencies.pydantic_model import CustomModel


class GetFrame(BaseModel):
    uploaded: str
    filename: str
    uuid: str


class Attachments(BaseModel):
    server_name: str
    filename: str


class CreateFrame(CustomModel):
    name: str
    description: str | None


class FrameResponse(BaseModel):
    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    short_url: str
    description: str
    likes: int = 0
    is_liked: bool = False


class Attachment(BaseModel):
    order: int
    url: str


class FrameOneResponse(FrameResponse):
    attachments: List[Attachment]


class FrameAllResponse(FrameResponse):
    preview: str


class Pagination(BaseModel):
    page: conint(ge=1) = 1
    count: conint(ge=1, le=50) = 10


T = TypeVar("T")


class PagedResponseSchema(GenericModel, Generic[T]):
    """Response schema for any paged API."""

    total: int
    page: int
    count: int
    results: List[T]
