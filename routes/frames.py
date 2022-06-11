import datetime
import uuid
from typing import List

from fastapi import UploadFile, File, HTTPException, APIRouter, Depends
from starlette.requests import Request
from starlette.responses import JSONResponse

from libraries.database import create_one_entry
from libraries.minio_handler import connect_to_minio
from libraries import database
from libraries.request_helper import need_auth
import pytz

frames_router = APIRouter()


@frames_router.post("/api/frames/", dependencies=[Depends(need_auth)])
async def post_frames(request: Request, files: List[UploadFile] = File(None)):
    if not files or len(files) > 15:
        return HTTPException(status_code=400, detail="Количество файлов должно быть в диапазоне от 0 до 15.")

    db = await database.get_database_instance()
    client = connect_to_minio()
    date = datetime.datetime.now().strftime("%Y%m%d")
    created_files = []

    if not client.bucket_exists(date):
        client.make_bucket(date)

    user_id = request.scope["user"]["id"]
    for file in files:
        if not file.filename.endswith(".jpg"):
            await db.disconnect()
            return HTTPException(status_code=400, detail="Файл должен иметь расширение jpg")

        file_uuid = uuid.uuid4().hex
        created_files.append({"servername": file_uuid, "filename": file.filename})
        await create_one_entry(db=db, tablename="inbox", values={"filename": file.filename, "uuid": file_uuid,
                                                                 "bucketname": date, "user_id": user_id})

        client.put_object(bucket_name=date, object_name=f"{file_uuid}.jpg", data=file.file, length=-1,
                          part_size=10485760)
    await db.disconnect()

    return JSONResponse(status_code=201, content=created_files)


@frames_router.get("/api/frames/{frame_uuid}", dependencies=[Depends(need_auth)])
async def get_frame(frame_uuid: str):
    db = await database.get_database_instance()
    client = connect_to_minio()
    date = datetime.datetime.now().strftime("%Y%m%d")
    frame = await database.get_filtered_entries(db=db, tablename="inbox", values={"uuid": frame_uuid})
    await db.disconnect()

    if not frame:
        raise HTTPException(status_code=400, detail="Такой uuid не найден.")

    item = [i for i in client.list_objects(date) if frame_uuid in i.object_name]
    time = item[0].last_modified.replace(tzinfo=pytz.timezone("Europe/Samara"))
    return JSONResponse(status_code=200, content={
        "response": {
            "uploaded": time.strftime("%d.%m.%Y %H:%M:%S"),
            "filename": frame[0]["filename"]
        }})


@frames_router.get("/api/frames/", dependencies=[Depends(need_auth)])
async def get_all_frames(request: Request):
    response = []
    client = connect_to_minio()
    user = request.scope["user"]["id"]
    date = datetime.datetime.now().strftime("%Y%m%d")
    db = await database.get_database_instance()

    for item in client.list_objects(date):
        replaced_string = item.object_name.replace(".jpg", "")
        frame = await database.get_filtered_entries(db=db, tablename="inbox", values={"user_id": user,
                                                                                      "uuid": replaced_string})
        if not frame:
            continue
        time = item.last_modified.replace(tzinfo=pytz.timezone("Europe/Samara"))
        response.append({
            "uploaded": time.strftime("%d.%m.%Y %H:%M:%S"),
            "filename": frame[0]["filename"],
            "uuid": str(item.object_name)
        })
    await db.disconnect()
    return JSONResponse(status_code=200, content={"response": response})


@frames_router.delete("/api/frames/{frame_uuid}", dependencies=[Depends(need_auth)])
async def delete_frame(request: Request, frame_uuid: str):
    client = connect_to_minio()
    date = datetime.datetime.now().strftime("%Y%m%d")
    db = await database.get_database_instance()
    user = request.scope["user"]["id"]
    frame = await database.get_filtered_entries(db=db, tablename="inbox", values={"uuid": frame_uuid, "user_id": user})

    if not frame:
        raise HTTPException(status_code=400, detail="Такой uuid не найден, или он не принадлежит вам.")

    client.remove_object(date, frame_uuid + ".jpg")
    await database.delete(db=db, tablename="inbox", where={"id": frame[0]["id"]})

    return JSONResponse(status_code=200, content={"response": "ok"})
