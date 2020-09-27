#!/usr/bin/env python3

import database
import sys
import os

def list_syncs():
    print(f"ID    Local path\tRemote path\tSync method".expandtabs(50))
    print("-"*110)
    data = database.get_syncs()
    for row in data:
        if row[3] is None:
            method = 'two-way sync'
        elif row[3] == 1:
            method = 'local -> remote'
        elif row[3] == 2:
            method = 'remote -> local'
        else:
            method = '???'
        print(f"{row[0]}    {row[1]}\t{row[2]}\t{method}".expandtabs(50))


def modify_sync(id,local,remote,type=None):
    database.modify_sync(id,local,remote,type)


def remove_syncs(id):
    database.remove_syncs(id)
    print(f'sync deleted!')


def sync(local, remote, sync_type=None):
    print(sync_type)
    if sync_type == '1':
        sync_type = 1
        a = ''
        while a != 'Y' and a != 'N' and a != 'y' and a != 'n':
            a = input(f"Are you sure? This will delete all remote file in the directory: {remote}? [Y/N]")
        if a=='Y' or a=='y':
            status = os.system("""rclone sync '{}' '{}' """.format(local,remote))
        else:
            status = -1
    elif sync_type == '2':
        sync_type = 2
        a = ''
        while a != 'Y' and a != 'N' and a != 'y' and a != 'n':
            a = input(f"Are you sure? This will delete all local file in the directory: {local}? [Y/N]")
        if a=='Y' or a=='y':
            status = os.system("""rclone sync '{}' '{}' """.format(remote, local))
        else:
            status = -1
    else:
        sync_type = None
        status = os.system("""rclone copy '{}' '{}' """.format(local, remote))

    if status == 0:
        database.add_sync(local, remote, sync_type)

        print(f'sync configurated between {local} and {remote}')
    else:
        print(f'An error happend :( We cannot able to transfer files from {local} to {remote}')


if __name__ == '__main__':
    database.init()
    if len(sys.argv) > 1:
        if sys.argv[1] == 'sync':
            if len(sys.argv) == 5:
                sync(sys.argv[2], sys.argv[3],sys.argv[4])
            elif len(sys.argv) == 4:
                sync(sys.argv[2],sys.argv[3])
            else:
                print('Not enough parameters! Usage: sync local_path remote_path [sync_type]')
        elif sys.argv[1] == 'list-sync':
            list_syncs()
        elif sys.argv[1] == 'remove-sync':
            if len(sys.argv) == 3:
                remove_syncs(sys.argv[2])
            else:
                print('Not enough parameters! Usage: remove-sync id')
        elif sys.argv[1] == 'help':
            print("="*14 + "  HELP  " + "="*14)
            print()
            print('Allowed methods:')
            print(" sync    \tSet a new sync\tusage: sync local_path remote_path [sync_type]")
            print(" list-sync\tlist configured sync")
            print(" remove-sync\tRemove a configured sync\tusage: remove-sync id")
            print()
            print('Allowed sync types:')
            print(" default\ttwo-way sync")
            print("   1    \tlocal -> remote")
            print("   2    \tremote -> local")
        else:
            print('Unexpected method! Allowed methods: sync, list-sync, remove-sync')
    else:
        print('Select a method: help, sync, list-sync, remove-sync')
