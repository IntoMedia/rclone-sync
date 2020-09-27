import sqlite3 as sl
from pathlib import Path
import os.path

folder = str(Path.home())+'/.config/rclone-sync'
dbname = folder+'/methods.db'
print(folder)

def init():
    if not os.path.exists(folder):
        os.makedirs(folder)

    con = sl.connect(dbname)
    with con:
        try:
            cursor = con.execute("SELECT version FROM VERSION")
            size = cursor.arraysize
        except:
            size = 0
        if size < 1:
            con.execute("""
                       CREATE TABLE IF NOT EXISTS METHODS (
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            event INTEGER,
                            file TEXT,
                            dir TEXT
                        );
            """)
            con.execute("""
                        CREATE TABLE IF NOT EXISTS SYNCS (
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            local_dir TEXT,
                            remote_dir TEXT
                        );
            """)
            con.execute("""
                        CREATE TABLE IF NOT EXISTS VERSION (
                            version INTEGER NOT NULL PRIMARY KEY
                        );
            """)
            con.execute("ALTER TABLE SYNCS ADD COLUMN type INTEGER;")

            sql_insert = 'INSERT INTO VERSION (version) values(?)'
            data_insert = [(2)]
            con.execute(sql_insert, data_insert)

        else:
            v = cursor.fetchone()
            # if v[0] == 2:


def get_syncs():
    con = sl.connect(dbname)
    with con:
        data = con.execute("SELECT id,local_dir,remote_dir,type FROM SYNCS")
        return data


def get_syncs_by_dir(path):
    con = sl.connect(dbname)
    sql = 'SELECT id,local_dir,remote_dir,type FROM SYNCS WHERE local_dir=?'
    data = [
        (path)
    ]
    with con:
        rows = con.execute(sql, data)
        return rows


def add_sync(local, remote,sync_type=None):
    sql = 'INSERT INTO SYNCS (local_dir, remote_dir, type) values(?, ?, ?)'
    data = [
        (local, remote, sync_type)
    ]
    con = sl.connect(dbname)
    with con:
        con.executemany(sql, data)


def remove_syncs(id):
    sql = 'DELETE FROM SYNCS WHERE id=?'
    data = [
        (id)
    ]
    con = sl.connect(dbname)
    with con:
        con.executemany(sql, data)


def get_methods():
    con = sl.connect(dbname)
    with con:
        rows = con.execute('SELECT id,event,dir,file FROM METHODS')
        return rows


def add_method(event, path, file):
    con = sl.connect(dbname)
    sql_insert = 'INSERT INTO METHODS (event, dir, file) values(?, ?, ?)'
    data_insert = [
        (event, path, file)
    ]
    with con:
        con.executemany(sql_insert, data_insert)


def delete_method(id):
    sql_del = 'DELETE FROM METHODS WHERE id=?'
    data_del = [id]
    con = sl.connect(dbname)
    with con:
        con.execute(sql_del, data_del)