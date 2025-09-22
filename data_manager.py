import json
import helpers
import time
import os.path
from shutil import copyfile
from filelock import FileLock

from file_observer import FileChangeHandler
from config import Config, get_config_file

_data_file_name = 'data.json'
_data_file = os.path.join(helpers.App_Data, _data_file_name)

def create_data_file():
    with open(_data_file, 'w') as f:
        json.dump({'files': []}, f)

def get_data_file():
    return _data_file

class DataManager:
    def __init__(self, target_dir):
        self.target_dir = target_dir
        self.read_data()
        self.lock = FileLock(f"{_data_file}.lock")

    def add_files(self, files):
        with self.lock:
            self.read_data()
            for file in files:
                file['last-update'] = 0
                file['deleted'] = False
                self.files.append(file)
            self.write_data()
        self.update_files()

    def remove_files(self, files):
        with self.lock:
            self.read_data()
            self.files = [f for f in self.files if f['name'] not in files]
            self.write_data()
        self.update_files()

    def update_target_dir(self, target_dir):
        assert self.target_dir != target_dir
        self.target_dir = target_dir
        self.reset_files()

    def read_data(self):
        with open(_data_file, 'r') as f:
            self.files = json.load(f)['files']
    
    def reset_files(self):
        with self.lock:
            self.read_data()
            for file in self.files:
                file['last-update'] = 0
            self.write_data()
        self.update_files()

    def write_data(self):
        assert self.lock.is_locked
        with open(_data_file, 'w') as f:
            json.dump({'files': self.files}, f)

    def check_folders_exist(self):
        """Check if folders for each file still exist and update deleted flags"""
        with self.lock:
            self.read_data()
            files_updated = False
            for file in self.files:
                path = file['path']
                folder = os.path.dirname(path)
                file_exists = os.path.exists(path)
                folder_exists = os.path.exists(folder)
                
                # If folder doesn't exist or file doesn't exist, mark as deleted
                if not folder_exists or not file_exists:
                    if not file.get('deleted', False):
                        file['deleted'] = True
                        files_updated = True
                        print(f"Marked file as deleted: {file['name']} (folder exists: {folder_exists}, file exists: {file_exists})")
                else:
                    # If folder and file exist, mark as not deleted
                    if file.get('deleted', False):
                        file['deleted'] = False
                        files_updated = True
                        print(f"Restored file: {file['name']}")
            
            if files_updated:
                self.write_data()
    
    def update_files(self):
        def file_exists_and_changed(last_check, file):
            if not os.path.isfile(file):
                return False
            time = os.path.getmtime(file)
            return time > last_check
        
        with self.lock:
            self.read_data()
            target_dir = self.target_dir
            curr_timestamp = int(time.time())

            files_updated = False
            for file in self.files:
                # Skip deleted files
                if file.get('deleted', False):
                    continue
                    
                path = file['path']
                name = file['name']
                file_last_update = file['last-update']
                target_file = os.path.join(target_dir, name)
                if file_exists_and_changed(file_last_update, path):
                    files_updated = True
                    copyfile(path, target_file)
                    file['last-update'] = curr_timestamp
            if files_updated:
                self.write_data()



class DataFileObserver:
    def __init__(self, config):
        self.config = config
        self.file_manager = DataManager(config.target_dir)
        self.postpone_period = Config().postpone_period
        self.last_update = 0
        self.data_watcher = FileChangeHandler([_data_file], self.on_data_update)
        self.config_watcher = FileChangeHandler([get_config_file()], self.on_config_update)

        # Check folder existence before setting up file watchers
        self.file_manager.check_folders_exist()
        
        # Only watch files that are not marked as deleted
        self.files = [os.path.normpath(file['path']) for file in self.file_manager.files if not file.get('deleted', False)]
        self.file_watcher = FileChangeHandler(self.files, self.on_file_update)

    def run(self):
        self.config_watcher.start()
        self.file_watcher.start()
        self.data_watcher.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.config_watcher.stop()
            self.file_watcher.stop()
        self.config_watcher.join()
        self.file_watcher.join()

    def on_file_update(self, _):
        current_time = time.time()
        if current_time - self.last_update < self.postpone_period:
            return
        self.last_update = current_time
        print('Files updated')
        time.sleep(self.postpone_period)
        self.file_manager.update_files()

    last_data_update = 0
    data_update_period = 1
    def on_data_update(self, _):
        if(time.time() - self.last_data_update < self.data_update_period):
            return
        self.last_data_update = time.time()
        time.sleep(self.data_update_period)
        print('Data file updated')
        
        # Check folder existence when data is updated
        self.file_manager.check_folders_exist()
        
        self.file_manager.read_data()
        # Only include non-deleted files
        new_files = [os.path.normpath(file['path']) for file in self.file_manager.files if not file.get('deleted', False)]
        changed = False
        for file in new_files:
            if file not in self.files:
                changed = True
        for file in self.files:
            if file not in new_files:
                changed = True
        if changed:
            print('list of files changed')
            self.files = new_files
            self.file_watcher.update_files(self.files)

    last_config_update = 0        
    def on_config_update(self, _):
        if(time.time() - self.last_config_update < .5):
            return
        self.last_config_update = time.time()
        time.sleep(.5)
        print('Config file updated')
        old_target = self.config.target_dir
        self.config.read_config()
        self.postpone_period = self.config.postpone_period
        if old_target != self.config.target_dir:
            self.file_manager.update_target_dir(self.config.target_dir)
        

def main():
    config = Config()
    observer = DataFileObserver(config)
    observer.run()

if __name__ == '__main__':
    main()
