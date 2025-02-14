from sys import argv
from shutil import copyfile
import config as cnf
import time
import os


def file_exists_and_changed(last_check, file):
    if not os.path.isfile(file):
        return False
    time = os.path.getmtime(file)
    return time > last_check



def update_files():
    config = cnf.Config(update_instance=True)
    target_dir = config.target_dir
    files = config.files

    curr_timestamp = int(time.time())
    config.last_check = curr_timestamp

    files_updated = False
    for file in files:
        path = file['path']
        name = file['name']
        last_update = file['last-update'] if 'last-update' in file else 0
        target_file = os.path.join(target_dir, name)
        if file_exists_and_changed(last_update, path):
            files_updated = True
            copyfile(path, target_file)
            file['last-update'] = curr_timestamp
            print(f'File {name} updated.')
    config.update_config()
    return files_updated


def main():
    update_files()
    

if __name__ == '__main__':
    main()