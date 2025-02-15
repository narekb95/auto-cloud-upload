import os
import json
import time

from enum import Enum
import helpers
from custom_tk import custom_messagebox
from filelock import FileLock

_config_file_name = 'config.json'
_config_file = os.path.join(helpers.App_Data, _config_file_name)

DEFAULT_CONFIG = {    
            "target": '',
            "registry": [],
            "last-update": 0,
            "update-frequency": 10,
            "scheduler-frequency": 60,
        }

def create_config_file(target_folder):
    class ResponseEnum(Enum):
        overwrite = 'overwrite'
        update_path = 'update path'
        skip = 'skip'
    
    response = ResponseEnum.overwrite
    if os.path.exists(_config_file):
        response = custom_messagebox("Error", "Config file already exists", ["overwrite", "update path", "skip"])
        response = ResponseEnum(response)
    
    config_data = {}
    if response == ResponseEnum.skip:
        return
    elif response == ResponseEnum.update_path:
        config_data = json.load(open(_config_file, 'r'))
        config_data['target'] = target_folder
        for file in config_data['registry']:
            del file['last-update']
    else:
        config_data = DEFAULT_CONFIG
        config_data['target'] = target_folder
    print(f"Creating config file at {_config_file}")
    os.makedirs(helpers.App_Data, exist_ok=True)
    with open(_config_file, 'w') as f:
        json.dump(config_data, f)

class Config:
    def __init__(self, update_instance=False):
        self.lock = FileLock(f"{_config_file}.lock")
        if update_instance:
            self.lock.acquire()
            self.locked = True
        else:
            self.locked = False

        config = self.read_config()
        self.target_dir = config['target']
        self.files = config['registry']
        self.last_update = config['last-update']
        self.update_frequency = config.get('update-frequency', 10)
        self.scheduler_frequency = config.get('scheduler-frequency', 60)


    def read_config(self):
        with open(_config_file, 'r') as f:
            return json.load(f)

    def reset_files(self):
        for file in self.files:
            file['last-update'] = 0
        self.last_update = 0

    # Only call if something really changed
    def update_config(self):
        assert self.locked
        self.last_update = int(time.time())
        with open(_config_file, 'w') as f:
            json.dump({
                'target': self.target_dir,
                'registry': self.files,
                'last-update': self.last_update,
                'update-frequency': self.update_frequency,
                'scheduler-frequency': self.scheduler_frequency
            }, f)
        self.lock.release()
