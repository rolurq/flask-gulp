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


def runner(command, f, ext):
    process = subprocess.Popen(command, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, shell=True)
    if not f.content:
        with open(f.filename) as fd:
            out, err = process.communicate(fd.read())
    else:
        out, err = process.communicate(f.content)

    if process.returncode:
        return f._replace(filename=None, content=err)
    else:
        _, fext = os.path.splitext(f.filename)
        dest = f.filename.replace(fext, ext)
        return f._replace(filename=dest, content=out)


@extension
def coffee(resources):
    bare = coffee.settings.get('bare')
    executable = coffee.settings.get('executable')

    command = "%s -c -s" % (executable or 'coffee')
    if bare:
        command = ' '.join((command, ' -b'))

    return (runner(command, f, '.js') for f in resources)


@extension
def cjsx(resources):
    bare = cjsx.settings.get('bare')
    executable = cjsx.settings.get('executable')

    command = "%s -c -s" % (executable or 'cjsx')
    if bare:
        command = ' '.join((command, '-b'))

    return (runner(command, f, '.js') for f in resources)


@extension
def less(resources):
    executable = less.settings.get('executable')
    return (runner("%s -" % (executable or 'lessc'), f, '.css')
            for f in resources)


@extension
def dest(resources):
    """
        This extension writes the `data` onto `filename` under the
        `output` directory in the settings. This functions closes the
        pipeline.
    """
    output = dest.settings.get('output')
    for f in resources:
        if f.filename:
            if output:
                base, _ = os.path.split(f.rel_name) if f.rel_name else ('', None)
                # create the new file in the same relative path
                dest_dir = os.path.join(output, base)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                _, tail = os.path.split(f.filename)
                filename = os.path.join(dest_dir, tail)
            else:
                filename = f.filename

            with open(filename, 'w') as fo:
                fo.write(f.content)
            yield f._replace(filename=filename, content=None)
