from sys import argv

from config import Config
import tkinter as tk
from tkinter import filedialog


def add_file(path, name):
    config = Config()
    extension = path.split('.')[-1]
    name = (f'{name}.{extension}').lower()
    file = next((file for file in config.files if file['name'].lower() == name), None)
    if file is not None:
        raise ValueError(f'File {name} already exists in auto-upload.')
    config.files.append({'path': path, 'name': name})
    config.update_config()

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

if __name__ == '__main__':
    path = argv[1] if len(argv) > 1 else ''

    root = tk.Tk()
    root.title("Active files")
    root.geometry("600x400")

    open_add_file_dialog(root, path)
    root.mainloop()

    # config = Config()

    # valid_name = False
    # while not valid_name:
    #     name = input('Target file name: ')
    #     valid_name = True
    #     try:
    #         add_file(path, name, config)
    #         print(f'File {name} added to auto-upload.')
    #     except ValueError as e:
    #         print(f'Value error: {e}')
    #         valid_name = False
    #     except Exception as e:
    #         print(f'Failed to add file {name}. Error: {e}')
    # input('Press Enter to exit...')
