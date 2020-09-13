#!/usr/bin/env python3

import sqlite3 as sl
import sys

con = sl.connect('methods.db')

def database():
    con = sl.connect('methods.db')
    with con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS METHODS (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                event INTEGER,
                file TEXT,
                dir TEXT
            );
        """)
    with con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS SYNCS (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                local_dir TEXT,
                remote_dir TEXT
            );
         """)

def list_syncs():
    with con:
        data = con.execute("SELECT * FROM SYNCS")
        for row in data:
            print(row)


def remove_syncs(id):
    sql = 'DELETE FROM SYNCS WHERE id=?'
    data = [
        (id)
    ]
    with con:
        con.executemany(sql, data)

    print(f'sync deleted!')


def sync(local,remote):
    sql = 'INSERT INTO SYNCS (local_dir, remote_dir) values(?, ?)'
    data = [
        (local, remote)
    ]
    with con:
        con.executemany(sql, data)

    print(f'sync configurated between {local} and {remote}')


if __name__ == '__main__':
    database()
    if len(sys.argv) > 1:
        if sys.argv[1] == 'sync':
            if len(sys.argv) > 3:
                sync(sys.argv[2],sys.argv[3])
            else:
                print('Not enough parameters! Usage: sync local_dir remote_dir')
        elif sys.argv[1] == 'list-sync':
            list_syncs()
        elif sys.argv[1] == 'remove-sync':
            if len(sys.argv) == 3:
                remove_syncs(sys.argv[2])
            else:
                print('Not enough parameters! Usage: remove-sync id')
        else:
            print('Unexpected method! Allowed methods: sync, list-sync, remove-sync')
    else:
        print('Select a method: sync - add a new sync, list-sync - list actual sync(s), remove-sync - remove an sync')
