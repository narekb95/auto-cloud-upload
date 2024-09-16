import winreg
import os
import sys

file_path = os.path.realpath(__file__)
dir_path = os.path.dirname(file_path)

python_path = sys.executable 

config_file = os.path.join(dir_path, 'config.txt')
uploader_path = os.path.join(dir_path, 'upload_files.py')
adder_path = os.path.join(dir_path, 'add_file.py')

config_arg = f'--config-file={config_file}'

user_key = winreg.HKEY_CURRENT_USER
key_path = r'Software\Classes\*\shell\AutoUpload'
uploader_key = winreg.CreateKey(user_key, key_path)
command_key = winreg.CreateKey(uploader_key, 'command')

command = f'{python_path} "{adder_path}" "%1" "{config_arg}"'

winreg.SetValue(uploader_key, '', winreg.REG_SZ, 'Add to Auto-upload')
winreg.SetValue(command_key, '', winreg.REG_SZ, command)



