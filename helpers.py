import os
import datetime
from threading import Timer

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

_data_path = os.getenv('LOCALAPPDATA')

App_Name = 'AutoUploader'
App_Data = os.path.join(_data_path, App_Name)
print(App_Data)

def read_arg(target : str, argv):
    arg =  next((a for a in argv if a.startswith(f'--{target}=')), None)
    return arg.split('=')[1] if arg != None else None

def timestamp_to_date(ts):
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d  %H:%M')


def file_exists_and_changed(self, last_check, file):
    if not os.path.isfile(file):
        return False
    time = os.path.getmtime(file)
    return time > last_check

def open_file(path):
    if os.path.exists(path):
        os.startfile(path)  # For Windows
    else:
        raise FileNotFoundError
    