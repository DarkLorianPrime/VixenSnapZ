from fastapi import HTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from routers.authorization.pydantic_models import AuthorizationModel
from routers.authorization.responses import Responses


async def validate_fields_not_empty(credentials: AuthorizationModel):
    if not credentials.username and not credentials.email:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail=Responses.NOT_EMAIL_NOT_USERNAME
        )

    return credentials
