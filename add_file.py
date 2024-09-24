from sys import argv

from config import Config

path = argv[1]
config = Config()

name = None
valid_name = False
while not valid_name:
    name = input('Target file name: ')
    file = next((file for file in config.files\
                  if file['name'].lower() == name.lower()), None)
    if file is not None:
        print(f'File {name} already exists in auto-upload.')
    else:
        valid_name = True

config.files.append({'path': path, 'name': name})
try:
    config.update_config()
    print(f'File {name} added to auto-upload.')
except Exception as e:
    print(f'Failed to add file {name}. Error: {e}')
input('Press Enter to exit...')