#!/usr/bin/env python3
import asyncio
import threading
from functools import partial
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import os
import sys
import json
import database
import option

sync_list = []
remotes_list = []
providers_list = []
tabs = {}
elements = {}
selected_id = -1
root = None
root_folder = None
new_window = None


def sync_listbox_onselect(event):
    global sync_list, root, elements, selected_id
    if len(elements['sync_listbox'].curselection()) > 0:
        selected_id = sync_list[elements['sync_listbox'].curselection()[0]][0]
        elements['local_txt'].delete(0, END)
        elements['remote_txt'].delete(0, END)
        elements['local_txt'].insert(0, sync_list[elements['sync_listbox'].curselection()[0]][1])
        elements['remote_txt'].insert(0, sync_list[elements['sync_listbox'].curselection()[0]][2])
        if sync_list[elements['sync_listbox'].curselection()[0]][3] is None:
            elements['type'].current(0)
        else:
            elements['type'].current(sync_list[elements['sync_listbox'].curselection()[0]][3])


def add_new_drive_listbox_onselect(event):
    global elements
    if len(elements['add_new_drive_list'].curselection()) > 0:
        elements['add_new_connection_name'].delete(0, END)
        elements['add_new_connection_name'].insert(0, providers_list[elements['add_new_drive_list'].curselection()[0]][
            'Name'])


def remove_drive():
    global elements
    if len(elements['remote_listbox'].curselection()) > 0:
        i = elements['remote_listbox'].curselection()[0]
        name = remotes_list[len(remotes_list) - i - 1]
        response = messagebox.askquestion(f"Delete {name}", f"Are you sure to delete {name}?",
                                          icon='warning')
        if response == "yes":
            status = os.system("""rclone config delete '{}' """.format(name))
            if status == 0:
                elements['remote_listbox'].delete(i)


def add_provider():
    global providers_list, new_window, elements, remotes_list
    provider = providers_list[elements['add_new_drive_list'].curselection()[0]]

    name = elements['add_new_connection_name'].get()

    new_window.destroy()

    status = os.system("""rclone config create '{}' '{}' """.format(name, provider['Prefix']))

    remotes_str = os.popen("rclone config dump").read()
    remotes_list_tmp = json.loads(remotes_str)
    remotes_list = []
    elements['remote_listbox'].delete(0, 'end')
    for t in remotes_list_tmp:
        remotes_list.append(t)
        elements['remote_listbox'].insert(0, f"{t}")


def add_new():
    global providers_list, new_window, elements
    providers_str = os.popen('rclone config providers').read()
    providers_list = json.loads(providers_str)

    new_window = Tk()

    new_window.geometry("620x360")
    new_window.title("Add new remote drive")

    label = Label(new_window, text="Connection Type:")
    label.pack()

    elements['add_new_drive_list'] = Listbox(new_window)
    i = 0
    for row in providers_list:
        elements['add_new_drive_list'].insert(i, f"{row['Description']}")
        i += 1
    elements['add_new_drive_list'].bind('<<ListboxSelect>>', add_new_drive_listbox_onselect)
    elements['add_new_drive_list'].pack(fill='both', expand=True)

    label2 = Label(new_window, text="Connection name:")
    label2.pack()

    elements['add_new_connection_name'] = Entry(new_window)
    elements['add_new_connection_name'].insert(0, '')
    elements['add_new_connection_name'].pack(fill='x')

    button = Button(new_window, text="Next", command=add_provider)
    button.pack()


def update_sync_list():
    elements['sync_listbox'].delete(0, 'end')
    data = database.get_syncs()
    for row in data:
        sync_list.append(row)
        if row[3] is None:
            method = 'two-way sync'
        elif row[3] == 1:
            method = 'local -> remote'
        elif row[3] == 2:
            method = 'remote -> local'
        else:
            method = '???'
        elements['sync_listbox'].insert(row[0], f"{row[1]} | {row[2]} | {method}")


def add_new_sync():
    global new_window, remotes_list
    if elements['type'].current() == 0:
        option.sync(elements['local_txt'].get(), elements['remote_txt'].get())
    else:
        if elements['type'].current() == 1:
            response = messagebox.askquestion(f"Are you sure?",
                                              f"Are you sure? This will delete all remote file in the remote directory!",
                                              icon='warning')
            if response == "yes":
                option.sync(elements['local_txt'].get(), elements['remote_txt'].get(), elements['type'].current())
        elif elements['type'].current() == 2:
            response = messagebox.askquestion(f"Are you sure?",
                                              f"Are you sure? This will delete all local file in the local directory!",
                                              icon='warning')
            if response == "yes":
                option.sync(elements['local_txt'].get(), elements['remote_txt'].get(), elements['type'].current())
    update_sync_list()


def modify_sync():
    global new_window, remotes_list, elements, selected_id
    if elements['type'].current() == 0:
        option.modify_sync(selected_id, elements['local_txt'].get(), elements['remote_txt'].get())
    else:
        if elements['type'].current() == 1:
            response = messagebox.askquestion(f"Are you sure?",
                                              f"Are you sure? This will delete all remote file in the remote directory!",
                                              icon='warning')
            if response == "yes":
                option.modify_sync(selected_id, elements['local_txt'].get(), elements['remote_txt'].get(),
                                   elements['type'].current())
        elif elements['type'].current() == 2:
            response = messagebox.askquestion(f"Are you sure?",
                                              f"Are you sure? This will delete all local file in the local directory!",
                                              icon='warning')
            if response == "yes":
                option.modify_sync(selected_id, elements['local_txt'].get(), elements['remote_txt'].get(),
                                   elements['type'].current())
    update_sync_list()


def remove_sync():
    global selected_id
    response = messagebox.askquestion(f"Delete", f"Are you sure to delete?",
                                      icon='warning')
    if response == "yes":
        option.remove_syncs(selected_id)
    update_sync_list()


def select_sync_folder():
    global new_window, remotes_list, elements

    path = filedialog.askdirectory(initialdir="/", title="Select folder")
    elements['local_txt'].delete(0, END)
    elements['local_txt'].insert(0, path)


def home():
    global root, sync_list, elements, remotes_list
    root = Tk()
    root.geometry("620x360")
    root.title("Sync")

    tab_control = ttk.Notebook(root)

    tabs["drives"] = ttk.Frame(tab_control)
    tabs["control"] = ttk.Frame(tab_control)

    frame = Frame(tabs["control"])
    frame.pack()

    list_frame = Frame(tabs["control"])
    list_frame.pack(side=TOP, fill='x')

    left_frame = Frame(tabs["control"])
    left_frame.pack(side=LEFT, padx=5, pady=5, fill='x', expand=True, anchor='n')

    right_frame = Frame(tabs["control"])
    right_frame.pack(side=RIGHT, padx=5, pady=5)

    label = Label(list_frame, text="Active syncs")
    label.pack()

    elements['sync_listbox'] = Listbox(list_frame)

    data = database.get_syncs()
    for row in data:
        sync_list.append(row)
        if row[3] is None:
            method = 'two-way sync'
        elif row[3] == 1:
            method = 'local -> remote'
        elif row[3] == 2:
            method = 'remote -> local'
        else:
            method = '???'
        elements['sync_listbox'].insert(row[0], f"{row[1]} | {row[2]} | {method}")

    elements['sync_listbox'].bind('<<ListboxSelect>>', sync_listbox_onselect)
    elements['sync_listbox'].pack(fill='x')

    elements['local_txt'] = Entry(left_frame)
    elements['local_txt'].insert(0, 'Local path')
    elements['local_txt'].pack(fill='x')

    elements['remote_txt'] = Entry(left_frame)
    elements['remote_txt'].insert(0, 'Remote path')
    elements['remote_txt'].pack(fill='x')

    elements['type'] = ttk.Combobox(left_frame, state="readonly",
                                    values=["Two way sync [Sync files between local and remote drive]",
                                            "local -> remote sync [Sync files only from local to remote drive]",
                                            "remote -> local sync [Sync files only from remote to local drive]",
                                            "Backup [Backup local files to remote drive]"])
    elements['type'].current(0)
    elements['type'].pack(padx=5, pady=5, fill='both')

    button = Button(right_frame, text="Select folder", command=select_sync_folder)
    button.pack(fill='x')

    button = Button(right_frame, text="Add new", command=add_new_sync)
    button.pack(fill='x')

    button = Button(right_frame, text="Save", command=modify_sync)
    button.pack(fill='x')

    button = Button(right_frame, text="Remove", command=remove_sync)
    button.pack(fill='x')

    # Drives
    left_frame = Frame(tabs["drives"])
    left_frame.pack(side=LEFT, padx=5, pady=5, fill='both', expand=True, anchor='n')

    right_frame = Frame(tabs["drives"])
    right_frame.pack(side=RIGHT, padx=5, pady=5)

    button = Button(right_frame, text="Add new drive", command=add_new)
    button.pack(fill='x')

    button = Button(right_frame, text="Remove drive", command=remove_drive)
    button.pack(fill='x')

    label = Label(left_frame, text="Remote drives")
    label.pack()

    elements['remote_listbox'] = Listbox(left_frame)

    try:
        remotes_str = os.popen("rclone config dump").read()
        remotes_list_tmp = json.loads(remotes_str)
        remotes_list = []
        for t in remotes_list_tmp:
            remotes_list.append(t)
            elements['remote_listbox'].insert(0, f"{t}")
    except:
        label = Label(left_frame, text="Please install rclone!")
        label.pack()

    elements['remote_listbox'].pack(expand=1, fill='both')

    tab_control.add(tabs["drives"], text="Remote drives")
    tab_control.add(tabs["control"], text="Active syncs")
    tab_control.pack(expand=1, fill="both")

    root.mainloop()


def load_paths(combo, remote_path):
    paths_str = os.popen("""rclone lsjson {}""".format(remote_path)).read()
    paths_all_data = json.loads(paths_str)
    paths = [remote_path]
    for pt in paths_all_data:
        if pt['IsDir']:
            paths.append(remote_path + pt['Path'])
    combo.configure(values=paths)


def save_folder_sync(path, t):
    global elements
    if elements[t]['chk_var'].get():
        if elements[t]['type'].current() > 0:
            option.sync(path, elements[t]['remote'].get())
        else:
            if elements['type'].current() == 1:
                response = messagebox.askquestion(f"Are you sure?",
                                                  f"Are you sure? This will delete all remote file in the remote directory!",
                                                  icon='warning')
                if response == "yes":
                    option.sync(path, elements[t]['remote'].get(), elements[t]['type'].current(), 'Y')
            elif elements['type'].current() == 2:
                response = messagebox.askquestion(f"Are you sure?",
                                                  f"Are you sure? This will delete all local file in the local directory!",
                                                  icon='warning')
                if response == "yes":
                    option.sync(path, elements[t]['remote'].get(), elements[t]['type'].current(), 'Y')


def folder_sync(path):
    global root_folder, remotes_list, tabs, elements
    root_folder = Tk()
    root_folder.geometry("360x420")
    root_folder.title("Sync")

    sync_dirs_cursor = database.get_syncs_by_dir(path)
    sync_dirs = {}
    for x in sync_dirs_cursor:
        tmp = x[2].split(':')
        sync_dirs[tmp[0] + '-' + x[1]] = x

    tab_control = ttk.Notebook(root_folder)
    try:
        remotes_str = os.popen("rclone config dump").read()
        remotes_list_tmp = json.loads(remotes_str)
        remotes_list = []
    except:
        label = Label(root_folder, text="Please install rclone!")
        label.pack()
        remotes_list_tmp = []
        remotes_list = []

    for t in remotes_list_tmp:
        elements[t] = {}
        remotes_list.append(t + ":/")

        tabs[t] = ttk.Frame(tab_control)

        right_bottom_frame = Frame(tabs[t])
        right_bottom_frame.pack(side=BOTTOM, padx=5, pady=5, anchor='se')

        right_frame = Frame(tabs[t])
        right_frame.pack(side=RIGHT, padx=5, pady=5, fill='x', expand=True, anchor='n')

        left_frame = Frame(tabs[t])
        left_frame.pack(side=LEFT, padx=5, pady=5, fill='x', anchor='n')

        elements[t]['chk_var'] = IntVar()
        elements[t]['chk'] = Checkbutton(left_frame, variable=elements[t]['chk_var'], text="sync this directory")
        elements[t]['chk'].pack(padx=5, pady=5, fill='both')

        label = Label(right_frame, text="")
        label.pack(padx=5, pady=5, fill='both')

        label = Label(left_frame, text="Local directory:", anchor='w')
        label.pack(padx=5, pady=5, fill='both')

        label = Label(right_frame, text=path, anchor='w')
        label.pack(padx=5, pady=5, fill='both')

        label = Label(left_frame, text="Remote directory:", anchor='w')
        label.pack(padx=5, pady=5, fill='both')

        elements[t]['remote'] = ttk.Combobox(right_frame, values=[t + ":/"])

        tt = threading.Thread(target=load_paths, args=(elements[t]['remote'], t + ":/"))
        tt.start()

        if t + '-' + path in sync_dirs.keys():
            elements[t]['chk'].select()
            elements[t]['remote'].set(sync_dirs[t + '-' + path][2])
        else:
            elements[t]['remote'].set("Pick a remote drive")
        elements[t]['remote'].pack(padx=5, pady=5, fill='both')

        label = Label(left_frame, text="Sync type:", anchor='w')
        label.pack(padx=5, pady=5, fill='both')

        elements[t]['type'] = ttk.Combobox(right_frame, state="readonly",
                                           values=["Two way sync [Sync files between local and remote drive]",
                                                   "local -> remote sync [Sync files only from local to remote drive]",
                                                   "remote -> local sync [Sync files only from remote to local drive]",
                                                   "Backup [Backup local files to remote drive]"])
        elements[t]['type'].current(0)
        elements[t]['type'].pack(padx=5, pady=5, fill='both')

        elements[t]['button'] = Button(right_bottom_frame, text="Save", command=partial(save_folder_sync, path, t))
        elements[t]['button'].pack(padx=5, pady=5, anchor='se')

        tab_control.add(tabs[t], text=t)

    tab_control.pack(expand=1, fill="both")

    root_folder.mainloop()


if __name__ == '__main__':
    database.init()
    if len(sys.argv) > 1:
        folder_sync(sys.argv[1])
    else:
        home()
