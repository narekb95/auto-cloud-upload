def read_arg(arg):
    # Read the parameters of syntax --arg=value
    # and return the value
    if not arg.startswith('--'):
        return None
    return arg.split('=')[1] 