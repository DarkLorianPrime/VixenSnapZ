import uuid
from typing import Any

from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_401_UNAUTHORIZED

from routers.authorization.service import Service


class Bearer(HTTPBearer):
    def __init__(self, *args: Any, **kwargs: Any):
        HTTPBearer.__init__(self, *args, auto_error=False, **kwargs)


class OAuthVerifier:
    async def __call__(self,
                       token: HTTPAuthorizationCredentials = Security(Bearer()),
                       service: Service = Depends(Service)):
        if token is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Credentials are not provided")

        token = token.credentials
        try:
            token = uuid.UUID(token)
        except ValueError:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Wrong token")

        user = await service.get_user_by_token(token=token)
        if user is not None:
            return user

        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token not found")


verifier = OAuthVerifier()
