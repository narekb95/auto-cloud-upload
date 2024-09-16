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



config_file = read_arg('config-file') or 'config.json'
config = read_config(config_file)

last_check = config['last-check'] if 'last-check' in config else 0
config['last-check'] = int(time.time())
update_config('config.json', config)

target_dir = config['target']
files = config['registry']

for file in files:
    path = file['path']
    name = file['name']
    target_file = target_dir + name
    if file_exists_and_changed(last_check, path):
        copyfile(path, target_file)
        log(f'{timestamp_to_date(time.time())} updated file \"{name}\".')