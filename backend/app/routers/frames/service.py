import datetime
import uuid
from typing import List, Optional, Sequence

from fastapi import Depends, UploadFile, HTTPException
from minio import Minio
from sqlalchemy import exists, select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST

from routers.authorization.pydantic_models import GetUser
from routers.frames.validators import filetype_validate
from storages.database import get_session
from storages.s3 import get_minio
from routers.authorization.models import User
from routers.categories.models import Category
from routers.frames.models import Frame, Attachments
from routers.frames.responses import Responses
import random
import string


def generate_short(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


class Service:
    def __init__(self, session: AsyncSession = Depends(get_session), minio: Minio = Depends(get_minio)):
        self.session = session
        self.minio = minio

    async def get_attachments_many(self, frames: Sequence[Frame]):
        frame_ids = [frame.id for frame in frames]
        stmt = select(Attachments).filter(Attachments.frame_id.in_(frame_ids)).distinct(Attachments.frame_id)
        response = await self.session.execute(stmt)
        response_scalar = response.scalars().all()

        return response_scalar

    async def get_attachments(self, frame_id: uuid.UUID, one: bool):
        stmt = select(Attachments).where(Attachments.frame_id == frame_id).order_by(Attachments.order)
        response = await self.session.execute(stmt)
        response_scalar = response.scalars()
        if one:
            return response_scalar.first()

        return response_scalar.all()

    async def get_frame(
            self,
            user_id: Optional[int] = None,
            frame_id: Optional[str] = None,
            one: Optional[bool] = True
    ):
        query = []
        if user_id is not None:
            query.append(Frame.owner_id == user_id)

        if frame_id is not None:
            query.append(Frame.id == frame_id)

        stmt = select(Frame).where(*query)
        result = await self.session.execute(stmt)

        scalar_result = result.scalars()
        if one:
            return scalar_result.first()

        return scalar_result.all()

    async def get_frames(self, user: User):
        response = []
        frames = await self.get_frame(user_id=user.id, one=False)
        if not frames:
            return response

        attachments = await self.get_attachments_many(frames=frames)
        attachments_dict = {attachment.frame_id: attachment.content for attachment in attachments}

        for frame in frames:
            frame_response = frame.fields
            frame_response["preview"] = attachments_dict.get(frame.id, None)
            response.append(frame_response)

        return response

    async def create_frame(
            self,
            user: GetUser,
            files: List[UploadFile],
            category_id: uuid.UUID,
            name: str,
            description: Optional[str] = None
    ):
        short_url = f"/s/{generate_short(12)}"

        create_data = {
            "name": name,
            "owner_id": user.id,
            "category": category_id,
            "short_url": short_url,
            "description": description
        }

        stmt = insert(Frame).values(**create_data).returning(Frame.id)
        frame = await self.session.execute(stmt)
        frame_id = frame.scalars().first()

        files_bodies = [
            {
                "order": num,
                "content": file,
                "frame_id": frame_id
            } for num, file in enumerate(files) if await filetype_validate(file.filename)
        ]

        stmt = insert(Attachments).returning(Attachments.content, Attachments.order)
        result = await self.session.execute(stmt, files_bodies)

        create_data.update(
            {
                "id": frame_id,
                "attachments": [
                    {
                        "url": attachment[0],
                        "order": attachment[1]
                    } for attachment in result.all()
                ]
            }
        )
        await self.session.commit()
        return create_data

    async def get_one_frame(self, frame_uuid: str):
        frame = await self.get_frame(frame_id=frame_uuid)

        if not frame:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.NOT_EXISTS_FRAME)

        attachments = await self.get_attachments(frame_id=frame.id, one=False)

        frame_response = frame.fields
        frame_response["attachments"] = [
            {
                "url": attachment.content,
                "order": attachment.order
            } for attachment in attachments
        ]
        return frame_response

    async def delete_frame(self, frame_uuid: str, user: User) -> None:
        frame = await self.get_frame(user_id=user.id, frame_id=frame_uuid, one=True)

        if not frame:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.NOT_YOUR_FRAME)

        bucket_name = datetime.datetime.now().strftime("%Y%m%d")
        self.minio.remove_object(bucket_name, frame_uuid)

        await self.session.delete(frame)
        await self.session.commit()

    async def is_category_exists(self, category_id):
        stmt = exists().where(Category.id == category_id).select()
        result = await self.session.execute(stmt)
        return result.scalars().first()
