from sys import argv
from helpers import update_config, read_config

path = argv[1]
name = input('Target file name: ')
config_file = 'C:\\Users\\Narek\\Documents\\workspace\\cloud-auto-upload\\config.json'
config = read_config(config_file)
config['registry'].append({'path': path, 'name': name})
update_config(config_file, config)