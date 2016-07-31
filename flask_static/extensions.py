import subprocess

from functools import wraps
import os

extensions = {}


def extension(f):
    """
        Decorator to create new extensions

        Each extension will receive a file name in `filename` and its content
        in `data`. The decorated function must return a tuple `(dest, ouput)`,
        where `ouput` will be the extension generated new data and `dest` the
        resulting file name.

        Also, under `<function_name>.settings` a dictionary is stored with the
        defined values from the extension initialization
    """
    # keep unwrapped function
    unwrapped = f

    @wraps(f)
    def wrapper(**kwargs):
        wrapper.settings = dict(kwargs)
        return unwrapped
    extensions[f.__name__] = wrapper
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
        _, ext = os.path.splitext(filename)
        dest = filename.replace(ext, '.js')
        return dest, out


@extension
def dest(filename, data):
    """
        This extension writes the `data` onto `filename` under the
        `destination` directory in the settings. This functions closes the
        pipeline.
    """
    destination = dest.settings.get('destination')
    if destination:
        if not os.path.exists(destination):
            os.mkdir(destination)
        _, tail = os.path.split(filename)
        filename = os.path.join(destination, tail)

    fo = open(filename, 'w')
    fo.write(data)
    fo.close()
