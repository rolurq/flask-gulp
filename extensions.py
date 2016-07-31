import subprocess

from functools import wraps
from os.path import splitext, join

extensions = {}

def extension(f):
    extensions[f.__name__] = f
    # keep unwrapped function
    unwrapped = f
    @wraps(f)
    def wrapper(**kwargs):
        wrapper.settings = dict(kwargs)
        return unwrapped
    return wrapper

@extension
def coffee(filename, data):
    command = ['coffee', '-c', '-s']
    bare = coffee.settings.get('bare')
    if bare:
        command.append('-b')

    process = subprocess.Popen(command, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate(data)

    if process.returncode:
        return None, err
    else:
        _,ext = splitext(filename)
        dest = filename.replace(ext, '.js')
        return dest, out

@extension
def dest(filename, data):
    destination = dest.settings.get('destination')
    if destination:
        filename = join(destination, filename)

    fo = open(filename, 'w')
    fo.write(data)
    fo.close()

