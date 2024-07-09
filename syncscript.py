import os
import shutil
import sys
import hashlib
import time
import argparse

#PROMPT COMMAND:
#python script_path source_folder destination_folder time_interval log_file_path
def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def log_action(log_file, action, path):
    message = f"{action}: {path}"
    print(message)
    with open(log_file, 'a') as f:
        f.write(message + '\n')

def sync_folders(source_folder, destination_folder, log_file):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        log_action(log_file, "Created destination folder", destination_folder)

    source_folder_items = set(os.listdir(source_folder))
    destination_folder_items = set(os.listdir(destination_folder))

    for item in destination_folder_items - source_folder_items:
        destination_folder_item = os.path.join(destination_folder, item)
        if os.path.isdir(destination_folder_item):
            shutil.rmtree(destination_folder_item)
        else:
            os.remove(destination_folder_item)
        log_action(log_file, "Removed file", destination_folder_item)

    all_synced = True
    for item in source_folder_items:
        source_folder_item = os.path.join(source_folder, item)
        destination_folder_item = os.path.join(destination_folder, item)
        if os.path.isdir(source_folder_item):
            if not sync_folders(source_folder_item, destination_folder_item, log_file):
                all_synced = False
        else:
            if not (os.path.exists(destination_folder_item) and 
                    os.path.getsize(source_folder_item) == os.path.getsize(destination_folder_item) and 
                    os.path.getmtime(source_folder_item) == os.path.getmtime(destination_folder_item) and
                    calculate_md5(source_folder_item) == calculate_md5(destination_folder_item)):
                if not os.path.exists(destination_folder_item):
                    shutil.copy2(source_folder_item, destination_folder_item)
                    log_action(log_file, "Created", destination_folder_item)
                else:
                    shutil.copy2(source_folder_item, destination_folder_item)
                    log_action(log_file, "Copied file", destination_folder_item)
                all_synced = False

    if all_synced:
        print("Syncing")
        return True
    else:
        print("Folders synced")
        return False

def main():
    parser = argparse.ArgumentParser(description="Periodically sync folders.")
    parser.add_argument("source_folder", help="Soulcer Folder.")
    parser.add_argument("destination_folder", help="Destination Folder.")
    parser.add_argument("time_interval", type=int, help="Time time_interval between syncs.")
    parser.add_argument("log_file_path", help="Log file path")

    arguments = parser.parse_args()

    source_folder = arguments.source_folder
    destination_folder = arguments.destination_folder
    time_interval = arguments.time_interval
    log_file = arguments.log_file_path

    if not os.path.exists(source_folder):
        print(f"Source folder '{source_folder}' does not exist.")
        sys.exit(1)

    while True:
        sync_folders(source_folder, destination_folder, log_file)
        time.sleep(time_interval)

if __name__ == "__main__":
    main()
