from sys import argv

from config import Config


def add_file(path, name, config):
    extension = path.split('.')[-1]
    name = (f'{name}.{extension}').lower()
    file = next((file for file in config.files if file['name'].lower() == name), None)
    if file is not None:
        raise ValueError(f'File {name} already exists in auto-upload.')
    config.files.append({'path': path, 'name': name})
    config.update_config()


path = argv[1]
config = Config()

valid_name = False
while not valid_name:
    name = input('Target file name: ')
    valid_name = True
    try:
        add_file(path, name, config)
        print(f'File {name} added to auto-upload.')
    except ValueError as e:
        print(f'Value error: {e}')
        valid_name = False
    except Exception as e:
        print(f'Failed to add file {name}. Error: {e}')
input('Press Enter to exit...')
