#!/usr/bin/env python3
import database
import os
from os.path import normpath
import pyinotify
import asyncio
import time

watchManager = pyinotify.WatchManager()
mask = pyinotify.IN_DELETE | pyinotify.IN_MODIFY | pyinotify.IN_CREATE | pyinotify.IN_OPEN | pyinotify.IN_ACCESS

serverSync = False
clientSync = False
lastRunning = 0
tryLastSync = 0
lastServerSync = 0
watchList = []


async def try_lasts():
    run_lasts()
    await sync_form_cloud()
    while True:
        run_lasts()
        await asyncio.sleep(60)
        set_watchers()
        await asyncio.sleep(60)


def run_lasts():
    global tryLastSync, serverSync
    if tryLastSync < time.time() - 30:
        tryLastSync = time.time()
        rows = database.get_methods()
        for row in rows:
            tryLastSync = time.time()
            if row[1] == 1:
                sync_copy(row[2], row[3])
            if row[1] == 2:
                sync_delete(row[2], row[3])

            database.delete_method((row[0]))


def set_watchers():
    global watchList
    data = database.get_syncs()
    for row in data:
        if row[1] not in watchList:
            print(f"watching: {row[1]}")
            watchList.append(row[1])
            watchManager.add_watch(row[1], rec=True, mask=mask, auto_add=True)


def sync_copy(path, file):
    while path.count('/') > 1:
        rows = database.get_syncs_by_dir(path)
        for row in rows:
            if row[3] is None or row[3] == 1:
                status = os.system("""rclone copy '{}' '{}' """.format(row[1], row[2]))

                if status != 0:
                    database.add_method(1, path, file)
        path = normpath(path + '/..')


def sync_delete(path, file):
    while path.count('/') > 1:
        rows = database.get_syncs_by_dir(path)
        for row in rows:
            if row[3] is None or row[3] == 1:
                a = file.replace(row[1], row[2])
                status = os.system("""rclone delete '{}' """.format(a))

                if status != 0:
                    database.add_method(2, path, file)
        path = normpath(path + '/..')


async def sync_form_cloud():
    global lastServerSync, serverSync, lastRunning, clientSync

    if lastServerSync < time.time() - 60:
        while clientSync or lastRunning > time.time() - 10:
            await asyncio.sleep(1)

        lastServerSync = time.time()

        rows = database.get_syncs()
        for row in rows:
            if row[3] is None or row[3] == 2:
                lastServerSync = time.time()
                serverSync = True
                status = os.system("""rclone sync '{}' '{}' """.format(row[2], row[1]))
                serverSync = False
        lastServerSync = time.time()


class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        global lastRunning, clientSync
        if not serverSync:
            lastRunning = time.time()
            clientSync = True
            sync_copy(event.path, event.pathname)
            clientSync = False

    def process_IN_DELETE(self, event):
        global lastRunning, clientSync
        if not serverSync:
            lastRunning = time.time()
            clientSync = True
            sync_delete(event.path, event.pathname)
            clientSync = False

    def process_IN_MODIFY(self, event):
        global lastRunning, clientSync
        if not serverSync:
            lastRunning = time.time()
            clientSync = True
            sync_copy(event.path, event.pathname)
            clientSync = False

    def process_IN_OPEN(self, event):
        if not serverSync:
            run_lasts()
            loop = asyncio.new_event_loop()
            loop.run_until_complete(sync_form_cloud())
            loop.close()

    def process_IN_ACCESS(self, event):
        if not serverSync:
            if event.dir:
                run_lasts()
                loop = asyncio.new_event_loop()
                loop.run_until_complete(sync_form_cloud())
                loop.close()


if __name__ == '__main__':
    database.init()

    notifier = pyinotify.ThreadedNotifier(watchManager, EventHandler())
    set_watchers()

    loop = asyncio.get_event_loop()
    task = loop.create_task(try_lasts())

    notifier.start()
    loop.run_forever()
