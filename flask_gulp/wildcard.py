import os
import glob


def wildcard(pattern):
    dirname, basename = os.path.split(pattern)
    if not glob.has_magic(pattern):
        if basename:
            if os.path.lexists(pattern):
                yield pattern, None
        elif os.path.isdir(dirname):
            yield pattern, None
        return

    if not dirname:
        if _isrecursive(basename):
            for _ in glob2(dirname, basename):
                yield _
        else:
            for _ in glob1(dirname, basename):
                yield _
        return

    if dirname != pattern and glob.has_magic(dirname):
        dirs = wildcard(dirname)
    else:
        dirs = [(dirname, None)]

    if glob.has_magic(basename):
        if _isrecursive(basename):
            glob_dir = glob2
        else:
            glob_dir = glob1
    else:
        glob_dir = glob0

    for dirname, _1 in dirs:
        for name, _2 in glob_dir(dirname, basename):
            yield os.path.join(dirname, name), os.path.join(_1 or '', _2)


def glob0(dirname, basename):
    if not basename:
        if os.path.isdir(dirname):
            yield basename, None
    else:
        if os.path.lexists(os.path.join(dirname, basename)):
            yield basename, None
    return


def glob1(dirname, pattern):
    for _ in glob.glob1(dirname, pattern):
        yield _, os.path.split(_)[1]


def glob2(dirname, pattern):
    yield pattern[:0], pattern[:0]
    for _ in _rlistdir(dirname):
        yield _, _


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
