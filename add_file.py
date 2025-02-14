from sys import argv

from config import Config
import tkinter as tk
from tkinter import filedialog

from update_files import update_files

import re

def add_file(path, name):
    name = name.strip()
    name_reg = re.compile(r'^[a-zA-Z0-9_\-\. ]+$')
    if path == '':
        raise ValueError('No file selected.')
    if  not name_reg.match(name):
        raise ValueError('Invalid file name.')

    config = Config()
    extension = path.split('.')[-1]
    name = (f'{name}.{extension}').lower()
    file = next((file for file in config.files if file['name'].lower() == name), None)
    if file is not None:
        raise ValueError(f'File {name} already exists in auto-upload.')
    config.files.append({'path': path, 'name': name})
    config.update_config()
    updated = update_files()
    assert(updated)

def update_path(path_var):
    newpath = filedialog.askopenfilename()
    path_var.set(newpath)


def handle_submit(path, name, error_var, dialog):
    try:
        add_file(path, name)
        dialog.destroy()
    except ValueError as e:
        error_var.set(e)

def open_add_file_dialog(dialog, path=''):

    path_var = tk.StringVar(value=path)
    error_var = tk.StringVar(value='')
    font_main = ("Arial", 14)

    # Frame for file selection
    frame_file = tk.Frame(dialog, bg="#f4f4f4")
    frame_file.pack(fill="x", padx=10, pady=10)

    path_button = tk.Button(frame_file, text="Select File", command=lambda: update_path(path_var))
    path_button.grid(row=0, column=0, padx=5, pady=5)

    path_label = tk.Label(frame_file, textvariable=path_var, font=font_main, bg="#f4f4f4", anchor="w", wraplength=400)
    path_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # Frame for file name input
    frame_name = tk.Frame(dialog, bg="#f4f4f4")
    frame_name.pack(fill="x", padx=10, pady=10)

    label_name = tk.Label(frame_name, text="File Name:", font=font_main, bg="#f4f4f4")
    label_name.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    entry_name = tk.Entry(frame_name, font=font_main, width=30)
    entry_name.grid(row=0, column=1, padx=5, pady=5, sticky="w")

   # Error Message Frame
    frame_error = tk.Frame(dialog, bg="#f4f4f4")
    frame_error.pack(fill="x", padx=10, pady=5)

    label_error = tk.Label(frame_error, textvariable=error_var, font=("Arial", 12), fg="red", bg="#f4f4f4")
    label_error.pack(anchor="w")

    submit_button = tk.Button(dialog, text="Submit", font=font_main, command=lambda: handle_submit(path_var.get(), entry_name.get(), error_var, dialog))
    submit_button.pack(pady=10)

    
    dialog.bind('<Escape>', lambda e: dialog.destroy())
    dialog.bind('<Return>', lambda e: handle_submit(path_var.get(), entry_name.get(), error_var, dialog))

def main():
    path = argv[1] if len(argv) > 1 else ''

    root = tk.Tk()
    root.title("Add file")
    root.geometry("600x400")

    open_add_file_dialog(root, path)
    root.mainloop()

if __name__ == '__main__':
    main()