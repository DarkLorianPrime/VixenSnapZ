def up():
    return """CREATE TABLE IF NOT EXISTS UserAccount(id SERIAL PRIMARY KEY, password VARCHAR(128), token varchar, username VARCHAR(150), registration_data timestamptz DEFAULT now())"""


def down():
    return """DROP TABLE UserAccount"""
