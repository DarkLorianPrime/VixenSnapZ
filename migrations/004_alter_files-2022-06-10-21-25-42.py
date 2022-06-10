def up():
    return """ALTER TABLE inbox ADD COLUMN user_id integer references useraccount (id)"""


def down():
    return """ALTER TABLE inbox DROP COLUMN user_id"""
