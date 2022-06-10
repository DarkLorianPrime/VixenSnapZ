def up():
    return """CREATE TABLE IF NOT EXISTS inbox(id SERIAL PRIMARY KEY, filename varchar, uuid varchar, bucketname varchar)"""


def down():
    return """DROP TABLE IF EXISTS inbox"""
