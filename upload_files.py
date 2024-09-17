from sys import argv
from shutil import copyfile
import json
import time
import os

from helpers import read_arg, log, timestamp_to_date, update_config, read_config

def file_exists_and_changed(last_check, file):
    if not os.path.isfile(file):
        return False
    time = os.path.getmtime(file)
    # print(f'File {file} time {time}, last check {last_check}')
    return time > last_check


config_file = read_arg('config-file', argv)
if config_file is None:
    raise Exception('Config file not provided.')

config = read_config(config_file)
target_dir = config['target']
files = config['registry']
curr_timestamp = int(time.time())
config['last-check'] = curr_timestamp

for file in files:
    path = file['path']
    name = file['name']
    last_update = file['last-update'] if 'last-update' in file else 0
    target_file = target_dir + name
    if file_exists_and_changed(last_update, path):
        copyfile(path, target_file)
        file['last-update'] = curr_timestamp
        print(f'File {name} updated.')
    else: 
        print(f'File {name} uptodate.')

update_config(config_file, config)
