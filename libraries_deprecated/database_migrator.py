import os
from datetime import datetime

import dotenv
import sqlalchemy
from sqlalchemy.engine import Engine

dotenv.load_dotenv("libraries_deprecated/.env")


def get_db_instance():
    url = sqlalchemy.engine.URL.create(
        "postgresql+psycopg2",
        username=os.getenv("user"),
        password=os.getenv("password"),
        host=os.getenv("host"),
        database=os.getenv("DB")
    )
    db = sqlalchemy.create_engine(url)
    db.connect()
    table_exists(db, "migrations")
    return db


def entry_exists(db: Engine, tablename: str, values: dict):
    query_where = ", ".join(f"{k}='{v}'" for k, v in values.items())
    query = "SELECT exists(select 1 FROM %s where %s)" % (tablename, query_where)
    data = db.execute(query)
    return get_one_result(data)[0]


def table_exists(db: Engine, tablename):
    query = "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = '%s');" % tablename
    data = db.execute(query)
    return get_one_result(data)[0]


def insert_migration(db: Engine, name: str):
    timestamp = datetime.now()
    query = """INSERT INTO migrations(name, timestamp) VALUES('%s', '%s')""" % (name, timestamp)
    db.execute(query)
    print(f"successfully inserted migration: {name}")


def delete_migration(db: Engine, name: str):
    print(f"successful migration rollback: {name}")
    if name.startswith("001_initial"):
        return
    name = name.split('.')[0]
    query = """DELETE FROM migrations WHERE name='%s'""" % name
    db.execute(query)


def get_all_results(result):
    return [element for element in result]


def get_filtered_entries(db: Engine, tablename: str, values: dict = None, orderby: str = None):
    query = "SELECT * FROM %s " % tablename
    if values is not None:
        query += "where %s" % ", ".join(f"{k}='{v}'" for k, v in values.items())
    if orderby is not None:
        query += f"order by {orderby}"
    data = db.execute(query)
    return get_all_results(data)


def get_one_result(result):
    for data in result:
        return data
