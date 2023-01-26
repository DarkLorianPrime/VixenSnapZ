import hashlib
import os
from typing import Union

import dotenv
from databases import Database


dotenv.load_dotenv("libraries_deprecated/.env")


async def get_database_instance() -> Database:
    """

    :return:
    """
    db = Database(f'postgres://{os.getenv("host")}/{os.getenv("DB")}', user=os.getenv("user"),
                  password=os.getenv("password"))
    await db.connect()
    return db


async def get_all_entries(db: Database, tablename) -> list:
    query = "SELECT * FROM %s" % tablename
    return await db.fetch_all(query)


async def get_filtered_entries(db: Database, tablename: str, values: dict = None, orderby: str = None) -> list:
    query = "SELECT * FROM %s " % tablename
    if values is not None:
        query += "where %s" % " and ".join(f"{k}='{v}'" for k, v in values.items())
    if orderby is not None:
        query += f"order by {orderby}"
    return await db.fetch_all(query)


async def create_one_entry(db: Database, tablename: str, values: dict) -> None:
    query = "INSERT INTO %s(%s) VALUES (:" % (tablename, ", ".join(k for k in values.keys())) + ", :".join(
        k for k in values.keys()) + ")"
    await db.execute(query, values)


async def table_exists(db: Database, tablename: str) -> bool:
    query = "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = '%s');" % tablename
    data = await db.fetch_one(query)
    return data[0]


async def create_many_entries(db: Database, tablename: str, values: list) -> None:
    if len(values) == 0:
        return
    await create_one_entry(db=db, tablename=tablename, values=values[0])
    values.pop(0)
    return await create_many_entries(db=db, tablename=tablename, values=values)


async def entry_exists(db: Database, tablename: str, where: dict) -> bool:
    query_where = " and ".join(f"{k}='{v}'" for k, v in where.items())
    query = "SELECT exists(select 1 FROM %s where %s)" % (tablename, query_where)
    data = await db.fetch_one(query)
    return data[0]


async def update(db: Database, tablename: str, values: Union[list, dict], where: dict) -> None:
    query_many_set = ""
    if type(values) == list:
        query_many_set = ", ".join([next(f"{k}='{v}'" for k, v in value.items()) for value in values])
    if type(values) == dict:
        query_many_set = [f'{key} = ' + ', '.join(f'{z} ' for z in value) for key, value in values.items()]
    query_where = " and ".join(f"{k}='{v}'" for k, v in where.items())
    query_many_set = ''.join(query_many_set)
    query = "UPDATE %s SET %s WHERE %s" % (tablename, query_many_set, query_where)
    await db.fetch_one(query)


async def delete(db: Database, tablename: str, where: dict) -> None:
    query_where = " and ".join(f"{k}='{v}'" for k, v in where.items())
    await db.fetch_one("DELETE FROM %s where %s" % (tablename, query_where))


class SHAPassword:

    def __init__(self, tablename):
        self.encoded_token = os.getenv("SHATOKEN").encode()
        self.table = tablename

    async def create_password(self, password):
        return hashlib.sha256(self.encoded_token + password.encode()).hexdigest()

    async def check_password(self, db, password, username):
        crypted_password = await self.create_password(password)
        return await entry_exists(db, self.table, {"password": crypted_password, "username": username})
