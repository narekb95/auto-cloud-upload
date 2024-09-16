import winreg
import subprocess
import os
import sys

file_path = os.path.realpath(__file__)
dir_path = os.path.dirname(file_path)

python_path = sys.executable 

config_file = os.path.join(dir_path, 'config.json')
uploader_path = os.path.join(dir_path, 'upload_files.py')
adder_path = os.path.join(dir_path, 'add_file.py')

config_arg = f'--config-file={config_file}'

# registry key for adding files to auto-upload
key_path = r'Software\Classes\*\shell\AutoUpload'
reg_command = f'{python_path} "{adder_path}" "%1" "{config_arg}"'
user_key = winreg.HKEY_CURRENT_USER
uploader_key = winreg.CreateKey(user_key, key_path)
command_key = winreg.CreateKey(uploader_key, 'command')
winreg.SetValue(uploader_key, '', winreg.REG_SZ, 'Add to Auto-upload')
winreg.SetValue(command_key, '', winreg.REG_SZ, reg_command)


# Task Scheduler for auto-uploadimport subprocess

# Define task parameters
task_name = "File Auto Uploader"
task_command = f'{python_path} "{uploader_path}" "{config_arg}"'

# Construct the schtasks command
schtasks_command = [
    "schtasks",
    "/Create",
    "/SC", "MINUTE", 
    "/TN", task_name,
    "/TR", task_command,
    "/F"  # Force create the task if it already exists
]

# Run the schtasks command
try:
    subprocess.run(schtasks_command, check=True)
    print(f"Task '{task_name}' created successfully.")
except subprocess.CalledProcessError as e:
    print(f"Failed to create task '{task_name}'. Error: {e}")