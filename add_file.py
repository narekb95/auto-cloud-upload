from sys import argv
from helpers import update_config, read_config, read_arg

path = argv[1]
name = input('Target file name: ')
config_file = read_arg('config-file', argv)
config = read_config(config_file)
config['registry'].append({'path': path, 'name': name})
try:
    update_config(config_file, config)
    print(f'File {name} added to auto-upload.')
except Exception as e:
    print(f'Failed to add file {name}. Error: {e}')
input('Press Enter to exit...')