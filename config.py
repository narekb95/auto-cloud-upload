import os
import json

import helpers

from tkinter import messagebox

_config_file_name = 'config.json'
_config_file = os.path.join(helpers.App_Data, _config_file_name)

def create_config_file(target_folder):
    # if the config file already exists, do nothing

    # show popup message to ask if the user wants to overwrite the file
    # create message box three options: overwrite, skip, update path
    # all options do nothing
    message = "A configuration file already exists. Do you want to overwrite it?"
    options = ['Overwrite', 'Skip', 'Update Path']
    result = messagebox.askquestion('Config file exists', message, icon='warning', options=options)
    messagebox.showinfo('Result', result)
    return

    if os.path.exists(_config_file):
        

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
