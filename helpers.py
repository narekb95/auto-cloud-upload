import os
import datetime

_data_path = os.getenv('LOCALAPPDATA')

App_Name = 'AutoUploader'
App_Data = os.path.join(_data_path, App_Name)

def read_arg(target : str, argv):
    arg =  next((a for a in argv if a.startswith(f'--{target}=')), None)
    return arg.split('=')[1] if arg != None else None

def timestamp_to_date(ts):
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d  %H:%M')


def open_file(path):
    if os.path.exists(path):
        os.startfile(path)  # For Windows
    else:
        raise FileNotFoundError

def get_files_in_dir(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def get_unsynced_files(config, data_man):
    files = {file['name'] for file in data_man.files}
    dir = config.target_dir
    
    files_in_dir = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    return dir, [f for f in files_in_dir if f not in files]