import sys

import importlib
import os
import shutil
import importlib.util
from datetime import datetime
from warnings import warn

from sqlalchemy.engine import Engine

from libraries.database_migrator import get_db_instance, table_exists, entry_exists, get_filtered_entries, \
    insert_migration, delete_migration
from libraries.exceptions import MigratorError
from libraries.files import check_file, check_file_end


def _import_module(name):
    warn("This module is deprecated and will be removed in a next release.", DeprecationWarning, stacklevel=2)
    spec = importlib.util.spec_from_file_location(name, f"migrations\\{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def first_migration(db: Engine) -> None:
    """
    :param db: The database to work
    :return: None.
    Description: Makes the first migration if it has not been done.
    """

    module = importlib.import_module(check_file("001_initial", "migrations")[0].split(".")[0])
    db.execute(module.up())


def prefirstmigrate() -> None:
    """
    :return: None.
    Description: Creates the basis for migration
    """

    if "migrations" not in os.listdir():
        os.mkdir("migrations")

    if not check_file("001_initial", "migrations"):
        shutil.copy("libraries/examples/migration_example_001.py",
                    f"migrations/001_initial-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.py")


def migrate(db: Engine, _) -> None:
    """
    :param _: Not used in this function
    :param db: The database to work
    :return: None.
    Description: Allows you to roll out new migrations, if they do not exist yet.
    """

    prefirstmigrate()

    if not table_exists(db, "migrations"):
        first_migration(db)

    files_list = check_file_end(".py", "migrations")
    files_list = list(map(lambda filename: filename.strip(".py"), files_list))
    for file in files_list:
        if entry_exists(db, "migrations", {"name": file}):
            continue

        module = importlib.import_module(file)
        db.execute(module.up())
        insert_migration(db, file)


def rollback_common(db: Engine) -> list:
    """
    :param db: The database to work
    :return: list of entries that can be rolled back.
    Description: General method
    """

    if not table_exists(db, "migrations"):
        raise MigratorError("No migration was applied.")

    data = get_filtered_entries(db, "migrations", None, "timestamp desc")
    return data


def rollback_all(db: Engine, _) -> None:
    """
    :param db: The database to work
    :param _: Not used in this function
    :return: None.
    Description: Rolls back all migrations
    """

    prefirstmigrate()
    data = rollback_common(db)
    for entry in data:
        module = importlib.import_module(entry[1])
        db.execute(module.down())
        delete_migration(db, entry[1])


def rollback(db: Engine, args: list) -> None:
    """
    :param db: The database to work
    :param args: Allows you to take the necessary arguments
    :return: None.
    Description: Rolls back the last migration, or if --step=N is specified, rolls back the last N migrations.
    """

    data = rollback_common(db)
    steps = 1

    if len(args) == 3:
        steps_timely = args[2].split("=")[1]
        if steps_timely.isdigit():
            steps = int(steps_timely)

    steps = len(data) if steps > len(data) else steps

    for step in range(0, steps):
        module = importlib.import_module(data[step][1])
        db.execute(module.down())
        delete_migration(db, data[step][1])


def refresh(db: Engine, args: list) -> None:
    """
    :param db: The database to work
    :param args: Not used in this function
    :return: None.
    Description: First deletes all migrations, then rolls them again.
    """

    try:
        rollback_all(db, args)
    except MigratorError as e:
        print(e)
    migrate(db, args)


def createmigration(_, args: list) -> None:
    """
    :param _: Not used in this function
    :param args: Allows you to take the necessary arguments
    :return: None
    """
    if len(args) != 3:
        raise MigratorError("Please specify the migration ID (for example: 001_cerera)")
    shutil.copy("libraries/examples/migration_example.py",
                f"migrations/{args[2]}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.py")


command = {
    "rollback": rollback,
    "reset": rollback_all,
    "migrate": migrate,
    "refresh": refresh,
    "makemigrations": createmigration
}


def main() -> None:
    sys.path.append("migrations")
    db = get_db_instance()
    args = sys.argv
    if len(args) < 2:
        raise MigratorError("Too few arguments.")

    command[args[1]](db, args)
    db.dispose()


if __name__ == "__main__":
    main()
