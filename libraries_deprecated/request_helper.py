from fastapi import HTTPException
from starlette.requests import Request

from libraries_deprecated import database


async def need_auth(request: Request):
    token = request.headers.get("authorization")
    if token is None:
        raise HTTPException(status_code=400, detail="Для этого действия требуется авторизация.")
    splited_token = token.split(" ")
    if len(splited_token) != 2:
        raise HTTPException(status_code=400, detail="Токен не найден или не действителен.")
    db = await database.get_database_instance()
    user = await database.get_filtered_entries(db=db, tablename="useraccount", values={"token": splited_token[1]})
    if not user:
        raise HTTPException(status_code=400, detail="Токен не найден или не действителен.")
    request.scope["user"] = user[0]
