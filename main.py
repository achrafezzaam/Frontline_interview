#!/usr/bin/env python3

import os
import sqlite3
from src import file_handler as fh
from src import database

basedir = os.path.abspath(os.path.dirname(__file__))
repo = os.path.join(basedir, "test/")
archive = os.path.join(basedir, "__ARCHIVE__/")
db = os.path.join(basedir, "src/my_database.db")

def scan(directory, dry_run=False):
    files = fh.find_inactive_files(directory, 2)
    if dry_run:
        for file in files:
            fh.archive_file("", file)

def purge(dry_run):
    if dry_run:
        fh.purge_archived_files("", 2)

def list():
    conn = sqlite3.connect(db)
    files = database.get_files_by_status(conn, 'archived')
    print("-"*40)
    for file in files:
        print(f"{file[1]}\t\tid: {file[0]}")
        print("-"*40)

def restore(file_id):
    conn = sqlite3.connect(db)
    fh.restore_archived_file(conn, file_id)

def delete(file_id):
    conn = sqlite3.connect(db)
    file = database.get_file_by_id(conn, file_id)
    os.remove(os.path.join(archive, file[1]))
    database.remove_file_record(conn, file_id)


exit_loop = True
while exit_loop:
    print("Welcome to the file manager:")
    print("- To get a list of all inactive files enter 1")
    print("- To archive all inactive files enter 2")
    print("- To delete the archived files enter 3")
    print("- To list all the archived files enter 4")
    print("- To restore an archived file enter 5")
    print("- To delete an archived file enter 6")
    print("- To quit the program enter 0")
    entry = input("==> ")
    match entry:
        case "1":
            scan(repo)
        case "2":
            scan(repo, True)
        case "3":
            purge(True)
        case "4":
            list()
        case "5":
            file_id = input("Choose an archived file to restore: ")
            restore(file_id)
        case "6":
            file_id = input("Choose an archived file to delete: ")
            delete(file_id)
        case "0":
            exit_loop = False
        case _:
            print("-"*40)
            print("Wrong entry. Please try again.")
            print("-"*40)
