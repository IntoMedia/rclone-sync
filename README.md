# Rclone Sync
#### Sync between your Linux computer and a cloud storage with rclone!

## BETA 4
![Logo](https://i.imgur.com/owxi5bi.png)
# How to use?
## With Nautilus, Nemo or Caja
- Firstly install [Rclone](https://rclone.org/downloads/)
- After install [Rclone-Sync](https://github.com/IntoMedia/rclone-sync/releases/)
- Open the Rclone-Sync: you can find it in the applications, the name: Sync

## In terminal
- Firstly install [Rclone](https://rclone.org/downloads/)
- Add a cloud drive to the Rclone: `rclone config`, and [follow the interactive setup process](https://rclone.org/docs/)!
- Download Rclone Sync to your computer, and make sure Python 3.6 and [PyNotify](https://github.com/seb-m/pyinotify) are installed. If not, you can use those commands: `sudo apt install python3.6` and `python3 -m pip install pyinotify`
- open Rclone Sync dir in your terminal, eg.: `cd ~/rclone-sync`
- Add sync to Rclone Sync: `./option.py sync local-dir/sync-dir remote:/` or you can sync just a specific remote directory:  `./option.py sync local-dir/sync-dir remote:/sync-dir`
- Start Rclone Sync: `./main.py`. Optionally you can add this command to the Startup Applications. The startup script are: `sh -c "cd ~/rclone-sync && ./main.py"`

![In Ubuntu](https://i.imgur.com/7ABvxKh.png)

![In Ubuntu](https://i.imgur.com/liPxyyb.png)

![In Linux Mint](https://i.imgur.com/O9AJ4Ok.png)

# How is work?
### local files
When a local file created, modified or deleted, the Rclone Sync immediatly catch this event, and sync the modifications on the cloud drive(s).
If the sync failed, it automatically try again in every 2 minutes.
### Cloud / remote files
The modifications on the remote cloud cannot detected, so the Rclone Sync use the [rclone sync](https://rclone.org/commands/rclone_sync/) command in the startup and after every minute when a local synced folder accessed. This method sync the cloud to the local machine, changing the local files only. Doesn't transfer unchanged files, testing by size and modification time or MD5SUM. local files is updated to match cloud, including deleting files if necessary.
### When you configurated the sync
All local file copyed to the cloud drive (if has any).


# Methods
- `./option.py help` show help
- `./option.py list-sync` list configurated sync(s)
- `./option.py sync  local_path remote-drive:/remote_path [sync_type]` add a new sync
- `./option.py remove-sync id` remove an configurated sync by ID

After you add or remove a sync, you need to restart the main.py!

# Supported cloud drives
All Rclone supported drive, sutch as: 
1Fichier,
Alias,
Amazon Drive,
Amazon S3,
Backblaze B2,
Box,
Cache,
Chunker,
Citrix ShareFile,
Crypt,
DigitalOcean Spaces,
Dropbox,
FTP,
Google Cloud Storage,
Google Drive,
Google Photos,
HTTP,
Hubic,
Jottacloud / GetSky.no,
Koofr,
Mail.ru Cloud,
Mega,
Memory,
Microsoft Azure Blob Storage,
Microsoft OneDrive,
OpenStack Swift / Rackspace Cloudfiles / Memset Memstore,
OpenDrive,
Pcloud,
premiumize.me,
put.io,
QingStor,
Seafile,
SFTP,
SugarSync,
Tardigrade,
Union,
WebDAV,
Yandex Disk

# Development
- [ ] improvement in multiple sync
- [x] Backup sync
- [x] Create Nautilus extension
- [x] Create Nemo extension
- [x] Create Caja extension
- [x] improvement in the GUI
- [x] start sync without log-out and log-in
