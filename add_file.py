from sys import argv
from helpers import update_config, read_config, read_arg

path = argv[1]
config_file = read_arg('config-file', argv)
config = read_config(config_file)

name = None
valid_name = False
while not valid_name:
    name = input('Target file name: ')
    file = next((file for file in config['registry']\
                  if file['name'].lower() == name.lower()), None)
    if file is not None:
        print(f'File {name} already exists in auto-upload.')
    else:
        valid_name = True

config['registry'].append({'path': path, 'name': name})
try:
    update_config(config_file, config)
    print(f'File {name} added to auto-upload.')
except Exception as e:
    print(f'Failed to add file {name}. Error: {e}')
input('Press Enter to exit...')