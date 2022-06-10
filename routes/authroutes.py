import datetime
import uuid

from fastapi import Form, APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from libraries.database import entry_exists, SHAPassword, get_database_instance, get_filtered_entries, create_one_entry

auth_router = APIRouter()


@auth_router.post("/api/registration/")
async def registration(username: str = Form(...), password: str = Form(...)):
    db = await get_database_instance()
    if await entry_exists(db, "UserAccount", {"username": username}):
        return HTTPException(status_code=404, detail={"error": "Account already exists"})
    hashed_pass = await SHAPassword("UserAccount").create_password(password)
    uuid_account = uuid.uuid4().hex
    await create_one_entry(db, "UserAccount", {"username": username, "password": hashed_pass, "token": uuid_account})
    return JSONResponse(status_code=201, content={"response": uuid_account})


@auth_router.post("/api/login/")
async def authorization(username: str = Form(...), password: str = Form(...)):
    db = await get_database_instance()
    if await SHAPassword("UserAccount").check_password(db, password, username):
        account = await get_filtered_entries(db, "useraccount", {"username": username})
        return JSONResponse(status_code=200, content={"response": str(account[0]["token"])})
    return HTTPException(status_code=404, detail={"error": "Account not found."})


@auth_router.get("/api/checkauth/")
async def isauth(request: Request):
    returned_dict = {k: str(v) for k, v in dict(request.scope["middleware"]["userdata"]).items()}
    returned_dict.pop("password")
    return JSONResponse(status_code=200, content={"response": returned_dict})
