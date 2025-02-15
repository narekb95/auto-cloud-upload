from sys import argv
import os

from config import Config
import tkinter as tk
from tkinter import filedialog

from update_files import update_files

import re

class SyncFile:
    def __init__(self, path, name):
        self.path = tk.StringVar(value=path)
        self.name = tk.StringVar(value=name)

def add_files(rows):
    config = Config(update_instance=True)
    for row in reversed(rows):
        if row.removed:
            continue
        file = row.file
        path = file.path.get()
        name = file.name.get() 
        extension = path.split('.')[-1]
        name = name.strip()
        name = (f'{name}.{extension}').lower()

        name_reg = re.compile(r'^[a-zA-Z0-9_\-\. ]+$')
        if path == '':
            row.err_var.set('No file selected.')
            continue
        if  not name_reg.match(name):
            row.err_var.set('Invalid file name.')
            continue

        file = next((file for file in config.files if file['name'].lower() == name), None)
        if file is not None:
            row.err_var.set(f'File {name} already exists in auto-upload.')
            continue

        config.files.append({'path': path, 'name': name, 'last-update': 0})
        row.removed = True

    config.update_config()

def update_path(path_var):
    newpath = filedialog.askopenfilename()
    path_var.set(newpath)

def shorten_path(path):
    return path if len(path) < 40 else f'{path[:10]}...{path[-30:]}'
 
def remove_removed_rows(rows):
    for row in rows:
        if row.removed:
            row.name_entry.destroy()
            row.path_label.destroy()
            row.remove_button.destroy()
    rows = [row for row in rows if not row.removed]
    for i, row in enumerate(rows):
        row.index = i
        row.name_entry.grid(row=i, column=0, padx=5, pady=5, sticky="w")
        row.path_label.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
        row.remove_button.grid(row=i, column=2, padx=5, pady=5)
    return rows
            

def open_add_file_dialog(dialog, files):    
    class Row:
        def __init__(self, file, index, root):
            self.file = file
            self.removed = False
            self.err_var = tk.StringVar(value='')
            self.display_path = tk.StringVar(value=shorten_path(file.path.get()))

            self.name_entry = tk.Entry(root, textvariable=file.name, font=("Arial", 10), width=30)
            self.name_entry.grid(row=index, column=0, padx=5, pady=5, sticky="w")

            self.path_label = tk.Label(root, textvariable=self.display_path, font=("Arial", 9), anchor="w", wraplength=400)
            self.path_label.grid(row=index, column=1, padx=5, pady=5, sticky="ew")

            self.remove_button = tk.Button(root, text="❌", font=("Arial", 6, ), fg="red", command=self.remove)
            self.remove_button.grid(row=index, column=2, padx=5, pady=5)

        def remove(self):
            self.name_entry.destroy()
            self.path_label.destroy()
            self.remove_button.destroy()
            self.removed = True

            
    dialog.grid_columnconfigure(0, weight=0)
    dialog.grid_columnconfigure(1, weight=1)
    dialog.grid_columnconfigure(2, weight=0)
    rows = [Row(file, i, dialog) for i, file in enumerate(files)]
    rows[0].name_entry.focus_set()
    rows[0].name_entry.selection_range(0, tk.END)

    def on_submit(rows):
        add_files(rows)
        if all(row.removed for row in rows):
            updated, _ = update_files()
            assert(updated)
            dialog.destroy()
        rows = remove_removed_rows(rows)
    
    def add_more_files():
        paths = filedialog.askopenfilenames()
        files = [SyncFile(path, get_name_without_extension(path))\
            for path in paths]
        for file in files:
            rows.append(Row(file, len(rows), dialog))
        pack_buttons()
                
    add_files_button = tk.Button(dialog, text="Add files", font=("Ariel", 9), command=add_more_files)
    submit_button = tk.Button(dialog, text="Submit", font=("Arial", 10), command=lambda rows = rows: on_submit(rows))

    
    def pack_buttons():
        add_files_button.grid(row=len(rows), column=0, columnspan=3, pady=10)
        submit_button.grid(row=len(rows)+1,column=0, columnspan=3, padx=20, pady=10, sticky="e")
    pack_buttons()

    dialog.bind('<Return>', lambda _, rows=rows : on_submit(rows))
    dialog.bind('<Escape>', lambda _: dialog.destroy())

def get_name_without_extension(path):
    return os.path.splitext(os.path.basename(path))[0] if path != '' else ''

def handle_add_file(root):
    path = filedialog.askopenfilenames()
    if(len(path) == 0):
        return
    files = [SyncFile(path, get_name_without_extension(path))\
        for path in path]
    
    dialog = tk.Toplevel()
    dialog.title("Add file")
    dialog.geometry("600x400")
    dialog.transient(root)
    dialog.grab_set()
    dialog.focus_set()
    open_add_file_dialog(dialog, files)
    root.wait_window(dialog)

def main():
    path = argv[1] if len(argv) > 1 else ''
    file_name = get_name_without_extension(path)

    root = tk.Tk()
    root.title("Add file")
    root.geometry("600x400")

    file = SyncFile(path, file_name)
    open_add_file_dialog(root, [file])
    root.mainloop()

if __name__ == '__main__':
    main()