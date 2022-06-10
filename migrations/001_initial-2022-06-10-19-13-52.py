def up():
    return "CREATE TABLE IF NOT EXISTS migrations(id SERIAL PRIMARY KEY, name text, timestamp timestamp)"


def down():
    return "DROP TABLE migrations"

