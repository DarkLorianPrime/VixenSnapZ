from pydantic import BaseModel


class GetFrame(BaseModel):
    uploaded: str
    filename: str
    uuid: str


class CreateFrame(BaseModel):
    server_name: str
    filename: str
