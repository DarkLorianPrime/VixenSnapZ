import uuid
from typing import List

from pydantic import BaseModel

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


class Attachment(BaseModel):
    order: int
    url: str


class FrameOneResponse(FrameResponse):
    attachments: List[Attachment]


class FrameAllResponse(FrameResponse):
    preview: str
