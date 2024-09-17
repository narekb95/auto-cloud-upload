import json
import datetime
def read_arg(target : str, argv):
    arg =  next((a for a in argv if a.startswith(f'--{target}=')), None)
    return arg.split('=')[1] if arg != None else None

def log(s):
    open('log.txt', 'a').write(s + '\n')

def timestamp_to_date(ts):
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')


def read_config(file):
    with open(file, 'r') as f: 
        data = f.read()
        config = json.loads(data)
    return config

def update_config(file, config):
    out = json.dumps(config)
    with open(file, 'w') as f:
        f.write(out)