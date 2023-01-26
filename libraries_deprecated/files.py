import os


def check_file(name, folder):
    return list(filter(lambda file: file.startswith(name), os.listdir(folder)))


def check_file_end(name, folder):
    return list(filter(lambda file: file.endswith(name), os.listdir(folder)))