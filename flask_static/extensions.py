import os
import subprocess
from functools import wraps


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


def runner(command, filename, data, ext):
    process = subprocess.Popen(command, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, shell=True)
    out, err = process.communicate(data)

    if process.returncode:
        return None, err
    else:
        _, fext = os.path.splitext(filename)
        dest = filename.replace(fext, ext)
        return dest, out


@extension
def coffee(filename, data):
    bare = coffee.settings.get('bare')
    executable = coffee.settings.get('executable')

    command = "%s -c -s" % (executable or 'coffee')
    if bare:
        command = ' '.join((command, ' -b'))

    return runner(command, filename, data, '.js')


@extension
def cjsx(filename, data):
    bare = cjsx.settings.get('bare')
    executable = cjsx.settings.get('executable')

    command = "%s -c -s" % (executable or 'cjsx')
    if bare:
        command = ' '.join((executable, '-b'))

    return runner(command, filename, data, '.js')


@extension
def less(filename, data):
    executable = less.settings.get('executable')
    return runner("%s -" % (executable or 'lessc'), filename, data, '.css')


@extension
def dest(filename, data):
    """
        This extension writes the `data` onto `filename` under the
        `output` directory in the settings. This functions closes the
        pipeline.
    """
    if filename:
        output = dest.settings.get('output')
        if output:
            if not os.path.exists(output):
                os.mkdir(output)
            _, tail = os.path.split(filename)
            filename = os.path.join(output, tail)

        with open(filename, 'w') as fo:
            fo.write(data)
    return filename, None
