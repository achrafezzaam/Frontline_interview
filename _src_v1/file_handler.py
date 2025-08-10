import os
import datetime
import sqlite3
from . import database

def find_inactive_files(directory, days_inactive):
    inactive_files = []

    content = os.listdir(directory)
    
    for file in content:
        file_path = directory + file
        access_time = os.path.getatime(file_path)
        last_access_time = datetime.datetime.fromtimestamp(access_time)
        today = datetime.datetime.now()
        delta = today - last_access_time
        check = datetime.timedelta(minutes=days_inactive)
        if delta > check:
            inactive_files.append(file)
    return inactive_files

def archive_file(db_conn, file_path):
    source = "test/" + file_path
    destination = "__ARCHIVE__/" + file_path
    try:
        os.rename(source, destination)
        print("The File was successfully archived")
    except OSError as e:
        print(f"Error moving file: {e}")

def purge_archived_files(db_conn, days_archived):
    files_to_del = []

    content = os.listdir("__ARCHIVE__/")

    for file in content:
        file_path = "__ARCHIVE__/" + file
        access_time = os.path.getatime(file_path)
        last_access_time = datetime.datetime.fromtimestamp(access_time)
        today = datetime.datetime.now()
        delta = today - last_access_time
        check = datetime.timedelta(minutes=days_archived)
        if delta > check:
            os.remove(file_path)

def restore_archived_file(db_conn, file_id):
    file = database.get_file_by_id(db_conn, file_id)
    destination = "test/" + file[1]
    source = "__ARCHIVE__/" + file[1]
    try:
        os.rename(source, destination)
        stat_info = os.stat(destination)
        current_mtime = stat_info.st_mtime
        os.utime(destination, times=(datetime.datetime.now().timestamp(), current_mtime))
        print("The File was successfully restored")
    except OSError as e:
        print(f"Error moving file: {e}")

