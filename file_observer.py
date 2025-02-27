from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from os import path
from threading import Thread

from os import path

class FolderDeletionHandler(FileSystemEventHandler):
    def __init__(self, folder, callback):
        super().__init__()
        self.callback = callback
        self.observer = Observer()
        self.update_watched_dirs(folder)


    def update_watched_dirs(self, folder):
        folder = path.normpath(folder)    
        self.observer.unschedule_all()
        self.folder = folder
        self.observer.schedule(self, path=self.folder, recursive=False)

    def on_deleted(self, event):
        Thread(target=self.callback, args=(event.src_path,)).start()

    def start(self):
        self.observer.start()
    
    def stop(self):
        self.observer.stop()

    def join(self):
        self.observer.join()

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, files, callback):
        super().__init__()
        self.callback = callback
        self.observer = Observer()
        self.update_files(files)

    def update_files(self, files):
        self.files = files
        self.update_watched_dirs()

    def update_watched_dirs(self):        
        self.observer.unschedule_all()
        WATCHED_DIRS = {path.dirname(f) for f in self.files}
        for directory in WATCHED_DIRS:
            self.observer.schedule(self, path=directory, recursive=False)

    def on_modified(self, event):
        if path.normpath(event.src_path) in self.files:
            Thread(target=self.callback, args=(event.src_path,)).start()

    def start(self):
        self.observer.start()
    
    def stop(self):
        self.observer.stop()

    def join(self):
        self.observer.join()