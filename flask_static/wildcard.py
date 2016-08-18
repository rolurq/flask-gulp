import os
import glob


def wildcard(pattern):
    dirname, basename = os.path.split(pattern)
    if not glob.has_magic(pattern):
        if basename:
            if os.path.lexists(pattern):
                yield pattern
        elif os.path.isdir(dirname):
            yield pattern
        return

    if not dirname:
        if _isrecursive(basename):
            for _ in glob2(dirname, basename):
                yield _
        else:
            for _ in glob.glob1(dirname, basename):
                yield _
        return

    if dirname != pattern and glob.has_magic(dirname):
        dirs = wildcard(dirname)
    else:
        dirs = [dirname]

    if glob.has_magic(basename):
        if _isrecursive(basename):
            glob_dir = glob2
        else:
            glob_dir = glob.glob1
    else:
        glob_dir = glob.glob0

    for dirname in dirs:
        for name in glob_dir(dirname, basename):
            yield os.path.join(dirname, name)


def glob2(dirname, pattern):
    yield pattern[:0]
    for _ in _rlistdir(dirname):
        yield _


def _rlistdir(dirname):
    if not dirname:
        dirname = os.curdir

    try:
        names = os.listdir(dirname)
    except os.error:
        return
    for name in names:
        if not name[0] == '.':
            yield name
            path = os.path.join(dirname, name) if dirname else name
            for rname in _rlistdir(path):
                yield os.path.join(name, rname)


def _isrecursive(pattern):
    return pattern == '**'

