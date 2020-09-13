#!/usr/bin/env python3
import sqlite3 as sl
import os
from os.path import basename
import pyinotify
import asyncio
import time

watchManager = pyinotify.WatchManager()
mask = pyinotify.IN_DELETE | pyinotify.IN_MODIFY | pyinotify.IN_CREATE | pyinotify.IN_OPEN | pyinotify.IN_ACCESS

serverSync = False
lastServerSync = 0


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


async def try_lasts():
    sync_form_cloud()
    while True:
        con = sl.connect('methods.db')
        with con:
            rows = con.execute('SELECT id,event,dir,file FROM METHODS')
            for row in rows:
                if row[1] == 1:
                    sync_copy(row[2], row[3])
                if row[1] == 2:
                    sync_delete(row[2], row[3])

                sql_del = 'DELETE FROM METHODS WHERE id=?'
                data_del = [(row[0])]
                con.execute(sql_del, data_del)

        #await asyncio.sleep(2)
        #sync_form_cloud()
        await asyncio.sleep(120)


def set_watchers():
    con = sl.connect('methods.db')
    with con:
        data = con.execute("SELECT id,local_dir FROM SYNCS")
        for row in data:
            print(f"watching: {row[1]}")
            watchManager.add_watch(row[1], rec=True, mask=mask, auto_add=True)


def add_method(event, path, file):
    con = sl.connect('methods.db')
    sql_insert = 'INSERT INTO METHODS (event, dir, file) values(?, ?, ?)'
    data_insert = [
        (event, path, file)
    ]
    with con:
        con.executemany(sql_insert, data_insert)


def sync_copy(path, file):
    con = sl.connect('methods.db')
    sql = 'SELECT id,local_dir,remote_dir FROM SYNCS WHERE local_dir=?'
    data = [
        (path)
    ]
    with con:
        rows = con.execute(sql, data)
        for row in rows:
            status = os.system("""rclone copy '{}' '{}' """.format(row[1], row[2]))

            if status != 0:
                add_method(1, path, file)


def sync_delete(path, file):
    con = sl.connect('methods.db')
    sql = 'SELECT id,local_dir,remote_dir FROM SYNCS WHERE local_dir=?'
    data = [
        (path)
    ]
    with con:
        rows = con.execute(sql, data)
        for row in rows:
            a = file.replace(row[1], row[2])
            status = os.system("""rclone delete '{}' """.format(a))

            if status != 0:
                add_method(2, path, file)


def sync_form_cloud():
    global lastServerSync, serverSync
    if lastServerSync < time.time()-60:
        lastServerSync = time.time()
        print("BG")
        con = sl.connect('methods.db')
        sql = 'SELECT id,local_dir,remote_dir FROM SYNCS'
        with con:
            rows = con.execute(sql)
            for row in rows:
                lastServerSync = time.time()
                serverSync = True
                status = os.system("""rclone sync '{}' '{}' """.format(row[2], row[1]))
                serverSync = False
        lastServerSync = time.time()


class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        if not serverSync:
            sync_copy(event.path, event.pathname)

    def process_IN_DELETE(self, event):
        if not serverSync:
            sync_delete(event.path, event.pathname)

    def process_IN_MODIFY(self, event):
        if not serverSync:
            sync_copy(event.path, event.pathname)

    def process_IN_OPEN(self, event):
        if not serverSync:
            if event.dir:
                sync_form_cloud()

    def process_IN_ACCESS(self, event):
        if not serverSync:
            if event.dir:
                sync_form_cloud()


if __name__ == '__main__':
    database()

    notifier = pyinotify.ThreadedNotifier(watchManager, EventHandler())
    set_watchers()

    loop = asyncio.get_event_loop()
    task = loop.create_task(try_lasts())

    notifier.start()
    loop.run_forever()
