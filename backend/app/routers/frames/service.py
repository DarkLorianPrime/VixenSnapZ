import datetime
import uuid
from typing import List, Optional, Sequence, Annotated, Dict, Any

from fastapi import Depends, UploadFile, HTTPException
from minio import Minio
from sqlalchemy import exists, select, insert, BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.functions import count
from starlette.status import HTTP_400_BAD_REQUEST

from routers.authorization.pydantic_models import GetUser, GetMe
from routers.frames.pydantic_models import Pagination
from routers.frames.validators import filetype_validate
from storages.database import get_session
from storages.s3 import get_minio
from routers.authorization.models import User
from routers.categories.models import Category
from routers.frames.models import Frame, Attachments, Likes
from routers.frames.responses import Responses
import random
import string


def generate_short(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


class BaseRepository:
    def __init__(
            self,
            session: Annotated[AsyncSession, Depends(get_session)],
            minio: Annotated[Minio, Depends(get_minio)]
    ):
        self.session = session
        self.minio = minio


class LikeRepository(BaseRepository):
    async def get(
            self,
            frame_id: uuid.UUID = None,
            user_id: uuid.UUID = None,
            query: Any = None,
            count_: bool = None,
            distinct: Any = None,
            one: bool = False
    ):
        queries = []
        selected_obj = [Likes]
        if count_:
            selected_obj = [
                Likes.frame_id,
                count(Likes.frame_id).label("count")
            ]

        stmt = select(*selected_obj)
        if count_:
            stmt = stmt.group_by(Likes.frame_id)

        if frame_id:
            queries.append(Likes.frame_id == frame_id)

        if user_id:
            queries.append(Likes.owner_id == user_id)

        if query is not None:
            queries.append(query)

        if distinct:
            stmt = stmt.distinct(distinct)

        stmt = stmt.where(*queries)
        result = await self.session.execute(stmt)
        if count_:
            return result.all()

        scalar_result = result.scalars()
        if not one:
            return scalar_result.all()

        return scalar_result.first()

    async def create(
            self,
            frame_id: uuid.UUID,
            user_id: uuid.UUID
    ):
        stmt = insert(Likes).values(frame_id=frame_id, owner_id=user_id, is_positive=True)
        await self.session.execute(stmt)

    async def delete(self, like: Likes):
        await self.session.delete(like)


class FramesRepository(BaseRepository):
    async def get(
            self,
            limit: int = None,
            offset: int = None,
            user_id: uuid.UUID = None,
            frame_id: uuid.UUID = None,
            one: bool = False
    ):
        queries = []
        stmt = select(Frame)

        if user_id:
            queries.append(Frame.owner_id == user_id)

        if frame_id:
            queries.append(Frame.id == frame_id)

        stmt = stmt.filter(*queries).order_by(Frame.id)
        if limit is not None and offset is not None:
            stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)

        scalar_result = result.scalars()
        if one:
            return scalar_result.first()

        return scalar_result.all()

    async def create(
            self,
            create_data: dict,
    ):
        stmt = insert(Frame).values(**create_data).returning(Frame.id)
        result = await self.session.execute(stmt)
        result_scalar = result.scalars()
        return result_scalar.first()

    async def delete(self, frame: Frame):
        await self.session.delete(frame)


class AttachmentsRepository(BaseRepository):
    async def get(
            self,
            query: BinaryExpression,
            query_2: BinaryExpression = None,
            distinct: Mapped = None,
            one: bool = False
    ):
        stmt = select(Attachments).filter(query)
        if query_2 is not None:
            stmt = stmt.where(query_2)

        if distinct:
            stmt = stmt.distinct(distinct)
        else:
            stmt = stmt.order_by(Attachments.order)

        print(stmt.compile(compile_kwargs={"literal_binds": True}))
        response = await self.session.execute(stmt)
        response_scalar = response.scalars()

        if one:
            return response_scalar.first()

        return response_scalar.all()

    async def create(
            self,
            create_data: List[Dict[str, Mapped]]
    ):
        stmt = insert(Attachments).returning(Attachments.content, Attachments.order)
        return await self.session.execute(stmt, create_data)

    async def delete(
            self,
    ):
        ...


class Service:
    def __init__(
            self,
            session: Annotated[AsyncSession, Depends(get_session)],
            minio: Annotated[Minio, Depends(get_minio)],
            frames: Annotated[FramesRepository, Depends()],
            attachments: Annotated[AttachmentsRepository, Depends()],
            likes: Annotated[LikeRepository, Depends()]
    ):
        self.session = session
        self.minio = minio
        self.frames = frames
        self.attachments = attachments
        self.likes = likes

    async def get_user_liked_frames(self, frames_id: Sequence[int], user_id: uuid.UUID):
        return await self.likes.get(
            query=Likes.frame_id.in_(frames_id),
            user_id=user_id
        )

    async def get_likes_many(self, frames_id: Sequence[int], user_id: uuid.UUID | None = None):
        return await self.likes.get(
            query=Likes.frame_id.in_(frames_id),
            user_id=user_id,
            count_=True,
        )

    async def get_attachments_many(self, frames_id: Sequence[int]):
        return await self.attachments.get(
            query=Attachments.frame_id.in_(frames_id),
            query_2=Attachments.order == 0,
            distinct=Attachments.frame_id
        )

    async def get_attachments(self, frame_id: uuid.UUID, one: bool):
        return await self.attachments.get(
            query=Attachments.frame_id == frame_id,
            one=one
        )

    async def get_frame(
            self,
            limit: int = None,
            offset: int = None,
            user_id: Optional[uuid.UUID] = None,
            frame_id: Optional[uuid.UUID] = None,
            one: Optional[bool] = True
    ):
        return await self.frames.get(
            user_id=user_id,
            frame_id=frame_id,
            one=one,
            limit=limit,
            offset=offset
        )

    async def get_frames(
            self,
            user: User | GetMe,
            me: bool,
            pagination: Pagination
    ):
        response = []
        pagination = {
            "offset": (pagination.page - 1) * pagination.count,
            "limit": pagination.count
        }

        frames_params = {"one": False, **pagination}
        if me:
            frames_params["user_id"] = user.id

        frames = await self.get_frame(**frames_params)
        if not frames:
            return response

        frames_id = [frame.id for frame in frames]

        attachments = await self.get_attachments_many(frames_id=frames_id)
        print({attachment.frame_id: attachment.order for attachment in attachments})
        attachments_dict = {attachment.frame_id: attachment.content for attachment in attachments}

        posts_likes = await self.get_likes_many(frames_id=frames_id)
        likes_dict = {like[0]: like[1] for like in posts_likes}

        liked_posts = await self.get_user_liked_frames(frames_id=frames_id, user_id=user.id)
        liked_posts_list = [like.frame_id for like in liked_posts]

        for frame in frames:
            frame_response = frame.fields
            frame_response["preview"] = attachments_dict.get(frame.id, None)
            frame_response["likes"] = likes_dict.get(frame.id, 0)
            frame_response["is_liked"] = frame.id in liked_posts_list
            response.append(frame_response)

        return response

    async def create_frame(
            self,
            user: GetUser,
            files: List[UploadFile],
            name: str,
            description: Optional[str] = None
    ):
        short_url = f"/s/{generate_short(12)}"

        create_data = {
            "name": name,
            "owner_id": user.id,
            "short_url": short_url,
            "description": description
        }

        frame_id = await self.frames.create(create_data)

        files_bodies = [
            {
                "order": num,
                "content": file,
                "frame_id": frame_id
            } for num, file in enumerate(files) if await filetype_validate(file.filename)
        ]

        result = await self.attachments.create(files_bodies)

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

    async def get_one_frame(self, user: GetMe | User, frame_uuid=None):
        frame = await self.get_frame(frame_id=frame_uuid)

        if not frame:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.NOT_EXISTS_FRAME)

        attachments = await self.get_attachments(frame_id=frame.id, one=False)
        post_likes = await self.get_likes_many(frames_id=[frame.id], user_id=user.id)
        is_liked = await self.get_user_liked_frames(frames_id=[frame.id], user_id=user.id)

        frame_response = frame.fields

        frame_response["likes"] = 0
        if post_likes:
            frame_response["likes"] = post_likes[0][1]
        frame_response["is_liked"] = bool(is_liked)
        frame_response["attachments"] = [
            {
                "url": attachment.content,
                "order": attachment.order
            } for attachment in attachments
        ]
        return frame_response

    async def delete_frame(
            self,
            frame_uuid: uuid.UUID,
            user: User | GetMe
    ) -> None:
        frame = await self.get_frame(user_id=user.id, frame_id=frame_uuid, one=True)

        if not frame:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.NOT_YOUR_FRAME)

        bucket_name = datetime.datetime.now().strftime("%Y%m%d")
        self.minio.remove_object(bucket_name, frame_uuid)

        await self.frames.delete(frame)
        await self.session.commit()

    async def is_category_exists(self, category_id):
        stmt = exists().where(Category.id == category_id).select()
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def toggle_like(
            self,
            frame_uuid: uuid.UUID,
            user_id: uuid.UUID
    ):
        like = await self.likes.get(
            frame_id=frame_uuid,
            user_id=user_id,
            one=True
        )
        if not like:
            await self.likes.create(
                frame_id=frame_uuid,
                user_id=user_id
            )

        else:
            await self.likes.delete(like)

        return await self.session.commit()
