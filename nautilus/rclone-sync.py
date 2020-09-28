#!/usr/bin/env python3
import subprocess
import sys
import gi
from gi.repository import GObject

if sys.argv[0] == 'nemo':
    gi.require_version('Nemo', '3.0')
    from gi.repository import Nemo as Nautilus
elif sys.argv[0] == 'caja':
    gi.require_version('Caja', '2.0')
    from gi.repository import Caja as Nautilus
else:
    gi.require_version('Nautilus', '3.0')
    from gi.repository import Nautilus


class MyItemExtension(GObject.GObject, Nautilus.MenuProvider):
    def get_file_items(self, window, files):
        if len(files) != 1:
            return
        f = files[0]
        if f.is_directory():
            menuitem = Nautilus.MenuItem(name='MyItem::SomeItem',
                                         label='Sync settings',
                                         tip='Sync settings',
                                         icon='/opt/rclone-sync/rclone-sync.png')

            menuitem.connect('activate', self.on_menu_item_clicked, files)
            return menuitem,
        return

    def on_menu_item_clicked(self, item, files):
        if len(files) != 1:
            return
        f = files[0]
        if f.is_directory():
            uri = f.get_uri().replace('file://', '')
            subprocess.call(["python3", "/opt/rclone-sync/gui.py",uri])