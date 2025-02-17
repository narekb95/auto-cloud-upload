import winreg
import subprocess
import os
import sys

import tkinter as tk
from tkinter import filedialog, messagebox

from data_manager import create_data_file, DataManager
from custom_tk import custom_messagebox, ResponseEnum

import config

def create_config(target_folder, handle_existing_config = False):
    if not handle_existing_config:
        try:
            config.create_config_file(target_folder, ResponseEnum.none)
            create_data_file()
        except FileExistsError:
            create_config(target_folder, handle_existing_config=True)
            return
    
    ops = ["overwrite", "update path", "skip"]
    response = custom_messagebox("Error", "Config file already exists", ops)
    response = ResponseEnum(response)
    config.create_config_file(target_folder, response)
    if response == ResponseEnum.overwrite:
        create_data_file()
    elif response == ResponseEnum.update_path:
        DataManager().reset_files()
        

def create_registry_key(python_path, adder_path):
    key_path = r'Software\Classes\*\shell\AutoUpload'
    reg_command = f'{python_path} "{adder_path}" "%1"'
    user_key = winreg.HKEY_CURRENT_USER
    uploader_key = winreg.CreateKey(user_key, key_path)
    command_key = winreg.CreateKey(uploader_key, 'command')
    print(f'Created registry key: {key_path}')
    winreg.SetValue(uploader_key, '', winreg.REG_SZ, 'Add to Auto-upload')
    winreg.SetValue(command_key, '', winreg.REG_SZ, reg_command)
    print(f'Created registry command: {reg_command} for key: {key_path}')

def create_task(pythonw_path, updater):
    task_name = "File Auto Uploader"
    task_command = f'{pythonw_path} "{updater}"'
    schtasks_command = [
        "schtasks",
        "/Create",
        "/SC", "ONLOGON", 
        "/TN", task_name,
        "/TR", task_command,
        "/F"  # Force create the task if it already exists
    ]

    try:
        subprocess.run(schtasks_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to create task '{task_name}'. Error: {e}")

    
def run_installer(target_folder):
    installer_path = os.path.realpath(__file__)
    installer_dir = os.path.dirname(installer_path)

    exec_path = sys.executable 
    python_folder = os.path.dirname(exec_path)
    pythonw_path = os.path.join(python_folder, 'pythonw3.exe')

    updater_path = os.path.join(installer_dir, 'data_manager.py')
    adder_path = os.path.join(installer_dir, 'add_file.py')

    create_registry_key(pythonw_path, adder_path)
    create_task(exec_path, updater_path)
    create_config(target_folder)
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
root.title("Auto Upload Installer")
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
