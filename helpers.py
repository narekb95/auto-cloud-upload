import json
import datetime
def read_arg(arg):
    # Read the parameters of syntax --arg=value
    # and return the value
    if not arg.startswith('--'):
        return None
    return arg.split('=')[1] 

def log(s):
    open('log.txt', 'a').write(s + '\n')

def timestamp_to_date(ts):
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')


def read_config(file):
    f = open(file, 'r')
    data = f.read()
    config = json.loads(data)
    f.close()
    return config

def update_config(file, config):
    out = json.dumps(config)
    f = open(file, 'w')
    f.write(out)
    f.close()