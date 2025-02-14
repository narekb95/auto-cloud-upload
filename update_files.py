from sys import argv
from shutil import copyfile
import config as cnf
import time
import os
import math

def file_exists_and_changed(last_check, file):
    if not os.path.isfile(file):
        return False
    time = os.path.getmtime(file)
    return time > last_check



# Returns true if some file changed after last update (in config) or after last check by caller (if provided)
def update_files(last_check = math.inf):
    config = cnf.Config(update_instance=True)
    target_dir = config.target_dir
    files = config.files

    curr_timestamp = int(time.time())

    files_updated = False
    for file in files:
        path = file['path']
        name = file['name']
        file_last_update = file['last-update']
        target_file = os.path.join(target_dir, name)
        if file_exists_and_changed(file_last_update, path):
            files_updated = True
            copyfile(path, target_file)
            file['last-update'] = curr_timestamp
            print(f'File {name} updated.')
    if files_updated:
        config.update_config()
    return (config.last_update > last_check or files_updated), curr_timestamp


def main():
    update_files()
    

if __name__ == '__main__':
    main()