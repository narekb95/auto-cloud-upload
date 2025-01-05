import os
import json

from enum import Enum
import helpers
from custom_tk import custom_messagebox

_config_file_name = 'config.json'
_config_file = os.path.join(helpers.App_Data, _config_file_name)

def create_config_file(target_folder):
    class ResponseEnum(Enum):
        overwrite = 'overwrite'
        update_path = 'update path'
        skip = 'skip'


    

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
        config_data = {
            "target": target_folder,
            "registry": []
        }
    print(f"Creating config file at {_config_file}")
    os.makedirs(helpers.App_Data, exist_ok=True)
    with open(_config_file, 'w') as f:
        json.dump(config_data, f)
        
class Config:
    def __init__(self):
        config = self.read_config()
        self.target_dir = config['target']
        self.files = config['registry']
        self.last_check = config['last-check'] if 'last-check' in config else 0

    def read_config(self):
        with open(_config_file, 'r') as f:
            return json.load(f)

    def update_config(self):
        with open(_config_file, 'w') as f:
            json.dump({
                'target': self.target_dir,
                'registry': self.files,
                'last-check': self.last_check
            }, f)
