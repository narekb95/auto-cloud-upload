import os
import json
import time

import helpers
from custom_tk import ResponseEnum
from filelock import FileLock

_config_file_name = 'config.json'
_config_file = os.path.join(helpers.App_Data, _config_file_name)

DEFAULT_CONFIG = {    
            "last-update": 0,
            "update-frequency": 10,
            "scheduler-frequency": 60,
            "postpone-period": .2,
        }

def get_default_config(target_folder):
    config_data = DEFAULT_CONFIG
    config_data['target'] = target_folder
    return config_data

def get_config_file():
    return _config_file

def create_config_file(target_folder, response):
    if not os.path.exists(_config_file):
        config_data = get_default_config(target_folder)
        with open(_config_file, 'w') as f:
            json.dump(config_data, f)
        return

    config_data = None
    if response == ResponseEnum.none:
        raise FileExistsError(f"Config file already exists at {_config_file}")
    elif response == ResponseEnum.overwrite:
        config_data = get_default_config(target_folder)
    elif response == ResponseEnum.update_path:
        config_data = json.load(open(_config_file, 'r'))
        config_data['target'] = target_folder
    elif response == ResponseEnum.skip:
        return

    print(f"Creating config file at {_config_file}")
    os.makedirs(helpers.App_Data, exist_ok=True)
    with open(_config_file, 'w') as f:
        json.dump(config_data, f)

class Config:
    def __init__(self):
        self.lock = FileLock(f"{_config_file}.lock")
        self.read_config()


    def read_config(self):
        config = None
        with open(_config_file, 'r') as f:
            config = json.load(f)
        
        self.target_dir = config['target']
        self.last_update = config['last-update']
        self.update_frequency = config.get('update-frequency')
        self.scheduler_frequency = config.get('scheduler-frequency')
        self.postpone_period = config.get('postpone-period')


    # Only call if something really changed
    def update_config(self):
        assert self.lock.is_locked
        self.last_update = int(time.time())
        with open(_config_file, 'w') as f:
            json.dump({
                'target': self.target_dir,
                'last-update': self.last_update,
                'update-frequency': self.update_frequency,
                'scheduler-frequency': self.scheduler_frequency,
                'postpone-period': self.postpone_period
            }, f)
