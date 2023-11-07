import datetime
import re
import uuid
from typing import Optional, Any

from fastapi import UploadFile
from sqlalchemy import Dialect, types
from sqlalchemy.sql.type_api import _T, TypeDecorator

from storages.s3 import get_minio


class File(TypeDecorator):
    cache_ok = True

    impl = types.String

    def __init__(self, is_need_folder: bool, bucket: str):
        super().__init__()
        self.is_need: bool = is_need_folder
        self.bucket: str = bucket

    def process_bind_param(self, value: Optional[UploadFile], dialect: Dialect) -> Any:
        folder = ""
        if self.is_need:
            folder = datetime.datetime.now().strftime("%Y%m%d")

        minio = get_minio()
        file_uuid = uuid.uuid4()
        file_type = re.search(r"(\.[0-9a-z]+)$", value.filename)
        filename = f"{folder}/{str(file_uuid)}"
        if file_type:
            filename += file_type.group(0)

        minio.put_object(
            bucket_name=self.bucket,
            object_name=filename,
            data=value.file,
            length=-1,
            part_size=10485760
        )

        return filename
