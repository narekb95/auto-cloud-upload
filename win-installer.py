import winreg
import subprocess
import os
import sys
import json

import tkinter as tk
from tkinter import filedialog, messagebox

def create_config_file(target_folder, config_file):
    config_data = {
        "target": target_folder,
        "registry": []
    }
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

def create_registry_key(python_path, adder_path, config_arg):
    key_path = r'Software\Classes\*\shell\AutoUpload'
    reg_command = f'{python_path} "{adder_path}" "%1" "{config_arg}"'
    user_key = winreg.HKEY_CURRENT_USER
    uploader_key = winreg.CreateKey(user_key, key_path)
    command_key = winreg.CreateKey(uploader_key, 'command')
    winreg.SetValue(uploader_key, '', winreg.REG_SZ, 'Add to Auto-upload')
    winreg.SetValue(command_key, '', winreg.REG_SZ, reg_command)

def create_task(pythonw_path, uploader_path, config_arg):
    task_name = "File Auto Uploader"
    task_command = f'{pythonw_path} "{uploader_path}" "{config_arg}"'
    schtasks_command = [
        "schtasks",
        "/Create",
        "/SC", "MINUTE", 
        "/TN", task_name,
        "/TR", task_command,
        "/F"  # Force create the task if it already exists
    ]

    try:
        subprocess.run(schtasks_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to create task '{task_name}'. Error: {e}")

    
def run_installer(target_folder):
    file_path = os.path.realpath(__file__)
    dir_path = os.path.dirname(file_path)

    python_path = sys.executable 
    python_folder = os.path.dirname(python_path)
    pythonw_path = os.path.join(python_folder, 'pythonw3.exe')

    config_file = os.path.join(dir_path, 'config.json')
    uploader_path = os.path.join(dir_path, 'upload_files.py')
    adder_path = os.path.join(dir_path, 'add_file.py')

    config_arg = f'--config-file={config_file}'

    create_registry_key(python_path, adder_path, config_arg)
    create_task(pythonw_path, uploader_path, config_arg)
    create_config_file(target_folder, config_file)
    show_popup()
    exit()

# UI
def show_popup():
    messagebox.showinfo("Installation", "Install Complete")

folder_path = None
def select_folder():
    global folder_path
    path = filedialog.askdirectory()
    if path:
        path = os.path.normpath(path)
        folder_path = path
        folder_label.config(text=f"Selected folder: {path}")

root = tk.Tk()
root.title("Folder Selector")
root.geometry("400x150")

# Create a label to display the selected folder
folder_label = tk.Label(root, text="No folder selected", wraplength=350)
folder_label.pack(pady=10)

select_button = tk.Button(root, text="Select Folder", command = select_folder)
select_button.pack(pady=10)

select_button = tk.Button(root, text="Install", command = lambda: run_installer(folder_path))
select_button.pack(pady=10)
# Start the main loop
root.mainloop()
